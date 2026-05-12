#!/usr/bin/env python3
import requests
import json
import argparse
from datetime import datetime, timedelta
import os

def get_contributions(username):
    """Busca contribuições do usuário via API do GitHub"""
    url = f"https://api.github.com/users/{username}/events"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    # Se tiver token, usa para aumentar limite de requisições
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'token {token}'
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erro ao buscar dados: {response.status_code}")
        return []
    
    events = response.json()
    
    # Conta contribuições por dia (últimos 365 dias)
    contributions = {}
    today = datetime.now()
    
    for event in events:
        if event['type'] in ['PushEvent', 'PullRequestEvent', 'IssuesEvent', 'CreateEvent']:
            date = datetime.strptime(event['created_at'][:10], '%Y-%m-%d')
            days_ago = (today - date).days
            if 0 <= days_ago < 365:
                contributions[days_ago] = contributions.get(days_ago, 0) + 1
    
    return contributions

def generate_svg(contributions, username, dark_mode=False):
    """Gera o SVG do gráfico de contribuições estilo Pacman"""
    
    # Cores
    if dark_mode:
        bg_color = "#0d1117"
        text_color = "#c9d1d9"
        empty_color = "#161b22"
    else:
        bg_color = "#ffffff"
        text_color = "#24292f"
        empty_color = "#ebedf0"
    
    levels = [
        {"color": "#216e39" if dark_mode else "#40c463", "min": 10},
        {"color": "#30a14e" if dark_mode else "#30a14e", "min": 6},
        {"color": "#40c463" if dark_mode else "#216e39", "min": 3},
        {"color": "#9be9a8" if dark_mode else "#9be9a8", "min": 1},
        {"color": empty_color, "min": 0}
    ]
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="850" height="180" viewBox="0 0 850 180">
    <rect width="100%" height="100%" fill="{bg_color}"/>
    <text x="20" y="30" font-family="Arial" font-size="14" fill="{text_color}">
        📊 {username}'s contribution graph (last 365 days)
    </text>
'''
    
    # Desenha os quadradinhos (7 colunas x 52 semanas)
    for week in range(52):
        for day in range(7):
            days_ago = (51 - week) * 7 + day
            if days_ago > 364:
                continue
                
            level = 4  # nível vazio
            if days_ago in contributions:
                count = contributions[days_ago]
                for i, lvl in enumerate(levels):
                    if count >= lvl["min"]:
                        level = i
                        break
            
            color = levels[level]["color"]
            x = 20 + week * 15
            y = 45 + day * 15
            
            svg += f'    <rect x="{x}" y="{y}" width="11" height="11" fill="{color}" rx="2"/>\n'
    
    # Adiciona legenda
    legend_x = 20 + 52 * 15
    svg += f'''
    <text x="{legend_x}" y="60" font-family="Arial" font-size="12" fill="{text_color}">Less</text>
'''
    
    for i, level in enumerate(levels[:-1]):
        svg += f'    <rect x="{legend_x + i * 17}" y="68" width="11" height="11" fill="{level["color"]}" rx="2"/>\n'
    
    svg += f'''    <text x="{legend_x + 68}" y="78" font-family="Arial" font-size="12" fill="{text_color}">More</text>
</svg>'''
    
    return svg

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--dark', action='store_true')
    args = parser.parse_args()
    
    print(f"Buscando contribuições para {args.username}...")
    contributions = get_contributions(args.username)
    
    if not contributions:
        print("Aviso: Nenhuma contribuição encontrada ou API limitada.")
    
    print(f"Gerando SVG com {len(contributions)} dias com contribuições...")
    svg = generate_svg(contributions, args.username, args.dark)
    
    with open(args.output, 'w') as f:
        f.write(svg)
    
    print(f"✅ SVG salvo em {args.output}")

if __name__ == "__main__":
    main()
