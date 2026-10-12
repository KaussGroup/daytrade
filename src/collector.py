import yfinance as yf
import requests
import feedparser
import urllib.parse
from datetime import datetime, timezone
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

ASSETS_MAP = {
    # Pré-Mercado ADRs Brasil em Nova York
    "EWZ": {"name": "EWZ (Brasil em NY)", "category": "Pré-Mercado NY", "icon": "🇧🇷"},
    "VALE": {"name": "Vale ADR (VALE)", "category": "Pré-Mercado NY", "icon": "⛏️"},
    "PBR": {"name": "Petrobras ADR (PBR)", "category": "Pré-Mercado NY", "icon": "🛢️"},
    "ITUB": {"name": "Itaú ADR (ITUB)", "category": "Pré-Mercado NY", "icon": "🏦"},
    
    # Índices e Futuros Globais
    "ES=F": {"name": "S&P 500 Futuro", "category": "Futuros EUA", "icon": "🇺🇸"},
    "NQ=F": {"name": "Nasdaq Futuro", "category": "Futuros EUA", "icon": "💻"},
    "^VIX": {"name": "VIX (Índice do Medo)", "category": "Volatilidade", "icon": "⚡"},
    
    # Commodities
    "TIO=F": {"name": "Minério de Ferro 62%", "category": "Commodities", "icon": "⛏️"},
    "BZ=F": {"name": "Petróleo Brent", "category": "Commodities", "icon": "🛢️"},
    "NG=F": {"name": "Gás Natural", "category": "Commodities", "icon": "🔥"},
    "GC=F": {"name": "Ouro (Gold)", "category": "Commodities", "icon": "🪙"},
    
    # Moedas, Juros & Ásia
    "USDBRL=X": {"name": "Dólar / Real (USD/BRL Pré-Mkt)", "category": "Pré-Mercado NY", "icon": "💵"},
    "DX-Y.NYB": {"name": "DXY (Dólar Global)", "category": "Pré-Mercado NY", "icon": "💵"},
    "USDMXN=X": {"name": "Dólar / Peso Mexicano (USD/MXN)", "category": "Forex Emergentes", "icon": "🇲🇽"},
    "EURUSD=X": {"name": "Euro / Dólar (EUR/USD)", "category": "Forex Global", "icon": "🇪🇺"},
    "^TNX": {"name": "Treasury 10A (Yield)", "category": "Juros EUA", "icon": "📈"},
    "^HSI": {"name": "Hang Seng (China/HK)", "category": "China & Ásia", "icon": "🇨🇳"},
    
    # Crypto & Apetite a Risco Global
    "BTC-USD": {"name": "Bitcoin (BTC/USD)", "category": "Crypto & Risco Global", "icon": "₿"}
}

NEWS_TOPICS = {
    "mercado_trabalho": {
        "title": "💼 Mercado de Trabalho (Payroll, Seguro-Desemprego, CAGED)",
        "query": "payroll seguro desemprego mercado de trabalho caged taxa de desemprego fed"
    },
    "geopolitica": {
        "title": "⚔️ Geopolítica & Guerras",
        "query": "guerra conflito geopolitica oriente medio ucrania"
    },
    "commodities": {
        "title": "🛢️ Petróleo, Gás & Minério",
        "query": "petroleo brent minerio ferro opec gas energia"
    },
    "tech_ai": {
        "title": "💻 Tech & Inteligência Artificial",
        "query": "inteligencia artificial tecnologia nvidia big tech chips"
    },
    "politica_br": {
        "title": "🏛️ Política & Brasília",
        "query": "brasilia governo lula congresso stf fiscal veto corrupcao"
    },
    "eua_china": {
        "title": "🌏 EUA & China (Índices & Bancos Centrais)",
        "query": "wall street fed juros banco central eua china economia"
    },
    "fundos_fluxo": {
        "title": "🏦 Fundos & Fluxo Institucional",
        "query": "blackrock fundos investimento capital estrangeiro b3"
    }
}

def get_market_assets():
    """Obtém cotações e variações recentes dos principais ativos mundiais."""
    results = []
    
    for ticker_symbol, meta in ASSETS_MAP.items():
        item = {
            "symbol": ticker_symbol,
            "name": meta["name"],
            "category": meta["category"],
            "icon": meta["icon"],
            "price": "N/D",
            "change_pct": 0.0,
            "change_str": "0.00%",
            "status": "NEUTRO"
        }
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Puxar com prepost=True para capturar cotações do pré-mercado de NY
            hist = ticker.history(period="5d", prepost=True)
            if not hist.empty and len(hist) >= 2:
                last_price = float(hist["Close"].iloc[-1])
                prev_price = float(hist["Close"].iloc[-2])
                change_pct = ((last_price - prev_price) / prev_price) * 100
                item["price"] = f"{last_price:,.2f}"
                item["change_pct"] = round(change_pct, 2)
                item["change_str"] = f"{change_pct:+.2f}%"
                if change_pct > 0.05:
                    item["status"] = "ALTA"
                elif change_pct < -0.05:
                    item["status"] = "BAIXA"
            elif not hist.empty:
                last_price = float(hist["Close"].iloc[-1])
                item["price"] = f"{last_price:,.2f}"
        except Exception:
            # Fallback seguro para não travar o relatório
            pass
            
        results.append(item)
        
    return results

def get_topic_news(max_per_topic=3):
    """Busca notícias das últimas horas divididas por categoria."""
    news_data = {}
    
    for key, topic in NEWS_TOPICS.items():
        items = []
        try:
            encoded_q = urllib.parse.quote(topic["query"])
            url = f"https://news.google.com/rss/search?q={encoded_q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            feed = feedparser.parse(resp.content)
            
            for entry in feed.entries[:max_per_topic]:
                # Limpar o título (Google News coloca '- Nome da Fonte' no final)
                title = entry.title
                source = "Notícia"
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    title = parts[0]
                    source = parts[1]
                    
                items.append({
                    "title": title,
                    "source": source,
                    "link": entry.link,
                    "published": entry.get("published", "")
                })
        except Exception:
            items = []
            
        news_data[key] = {
            "title": topic["title"],
            "items": items
        }
        time.sleep(0.1) # cortesia para evitar rate limit
        
    return news_data

def get_economic_calendar():
    """Gera a régua de horários críticos de volatilidade para o day trade."""
    # Eventos padrão de monitoramento de risco intradiário
    return [
        {"time": "09:00", "event": "Abertura do Contrato Futuro de Índice (WIN) e Dólar (WDO)", "impact": "ALTO", "note": "Primeiro leilão e volatilidade de gap"},
        {"time": "09:30", "event": "Pré-mercado de Ações nos EUA & Indicadores Econômicos", "impact": "MÉDIO", "note": "Definição de tração inicial"},
        {"time": "10:00", "event": "Abertura do Mercado à Vista B3 (Ações Petrobras, Vale, Bancos)", "impact": "MÁXIMO", "note": "Entrada do fluxo institucional e arbitragens"},
        {"time": "10:30", "event": "Abertura das Bolsas de Nova York (NYSE e Nasdaq)", "impact": "MÁXIMO", "note": "Pico de volume e correlação com S&P"},
        {"time": "14:00 - 15:30", "event": "Discursos de autoridades do Federal Reserve / BCB", "impact": "MÉDIO", "note": "Cuidado com violinadas nas taxas de juros"},
        {"time": "17:00", "event": "Fechamento do Mercado à Vista e Call de Fechamento", "impact": "ALTO", "note": "Leilão de encerramento das ações"}
    ]

def get_labor_indicators():
    """Compila os principais dados de mercado de trabalho e emprego (EUA & Brasil)."""
    return [
        {
            "name": "Non-Farm Payroll (NFP)",
            "country": "🇺🇸 EUA",
            "impact": "MÁXIMO",
            "frequency": "1ª Sexta-feira do mês (10:30 BRT)",
            "rule": "Acima do esperado = Fed mantém juros altos (Dólar ▲, Bolsa ▼). Abaixo do esperado = Corte de juros (Dólar ▼, Bolsa ▲)."
        },
        {
            "name": "Pedidos de Seguro-Desemprego (Jobless Claims)",
            "country": "🇺🇸 EUA",
            "impact": "ALTO",
            "frequency": "Todas as quintas-feiras (10:30 BRT)",
            "rule": "Termômetro semanal de demissões. Pedidos altos = mercado esfriando. Pedidos baixos = mercado aquecido."
        },
        {
            "name": "Taxa de Desemprego (IBGE / PNAD)",
            "country": "🇧🇷 Brasil",
            "impact": "ALTO",
            "frequency": "Mensal / Trimestral",
            "rule": "Desemprego em queda pressiona salários e setor de serviços, influenciando decisões de alta ou corte da Selic pelo Copom."
        },
        {
            "name": "CAGED (Emprego Formal)",
            "country": "🇧🇷 Brasil",
            "impact": "MÉDIO",
            "frequency": "Divulgação mensal pelo Ministério do Trabalho",
            "rule": "Saldo líquido de contratações formais com carteira assinada. Baliza a força do consumo interno na B3."
        }
    ]

def collect_all():
    """Executa a coleta unificada."""
    market_assets = get_market_assets()
    news = get_topic_news(max_per_topic=3)
    calendar = get_economic_calendar()
    labor = get_labor_indicators()
    
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "assets": market_assets,
        "news": news,
        "calendar": calendar,
        "labor_indicators": labor
    }

if __name__ == "__main__":
    print("Testando coletor...")
    res = collect_all()
    print(f"Coletados {len(res['assets'])} ativos e {len(res['news'])} categorias de notícias.")
