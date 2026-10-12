import os
import json
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

# Drivers típicos de mercado associados à direção de cada ativo
ASSET_CATALYST_TEMPLATES = {
    "ES=F": {
        "up": "Apetite por risco em NY impulsionado por resultados corporativos e alívio na curva de juros.",
        "down": "Aversão a risco em Wall Street com temores de juros restritivos do Fed e realização de lucros."
    },
    "NQ=F": {
        "up": "Rally no setor de tecnologia, semicondutores e inteligência artificial puxando os futuros.",
        "down": "Pressão vendedora em Big Techs e rotação defensiva de carteiras institucionais."
    },
    "TIO=F": {
        "up": "Estímulos fiscais na infraestrutura da China e queda nos estoques portuários impulsionam o minério.",
        "down": "Cautela com demanda siderúrgica chinesa e restrições ambientais em usinas reduzem o minério."
    },
    "BZ=F": {
        "up": "Tensões geopolíticas com risco de interrupção de oferta no Oriente Médio e disciplina da OPEP+.",
        "down": "Aumento dos estoques de petróleo e preocupações com desaceleração do consumo global."
    },
    "NG=F": {
        "up": "Projeções climáticas de maior demanda por aquecimento/energia e aperto em gasodutos.",
        "down": "Armazenamento elevado de gás natural e temperaturas amenas limitam as cotações."
    },
    "DX-Y.NYB": {
        "up": "Moeda americana fortalecida globalmente com postura hawkish do Fed e busca por porto seguro.",
        "down": "Desvalorização global do dólar com apetite por moedas emergentes e ativos de risco."
    },
    "^TNX": {
        "up": "Yields dos Treasuries em alta com dados de resiliência econômica e cautela com inflação nos EUA.",
        "down": "Yields dos títulos americanos recuam com busca por renda fixa soberana e alívio inflacionário."
    },
    "^HSI": {
        "up": "Pacote de liquidez do Banco Central Chinês (PBoC) e avanço de ações de tecnologia em Hong Kong.",
        "down": "Dados de atividade industrial da China abaixo do esperado geram cautela em bolsas asiáticas."
    },
    "^N225": {
        "up": "Enfraquecimento do iene favorece exportadoras japonesas e atrai fluxo estrangeiro a Tóquio.",
        "down": "Apreciação do iene e realização de lucros após recentes máximas no mercado japonês."
    },
    "EWZ": {
        "up": "Pré-mercado do EWZ (Ibovespa em NY) em alta, indicando fluxo comprador de fundos estrangeiros.",
        "down": "Pré-mercado do EWZ em baixa, apontando para venda de ações brasileiras por investidores globais."
    },
    "VALE": {
        "up": "ADR da Vale disparando no pré-mercado de NY, antecipando forte pressão compradora em VALE3.",
        "down": "ADR da Vale recuando no pré-mercado de NY, indicando abertura defensiva para mineradoras na B3."
    },
    "PBR": {
        "up": "ADR da Petrobras em alta no pré-mercado de Wall Street, dando suporte de abertura a PETR4.",
        "down": "ADR da Petrobras em queda no pré-mercado de NY, pressionando setor de energia e estatais."
    },
    "ITUB": {
        "up": "ADR do Itaú firme no pré-mercado de NY, apontando para sustentação no setor bancário e financeiro.",
        "down": "ADR do Itaú em baixa no pré-mercado de NY, sinalizando cautela institucional com bancos na B3."
    },
    "^VIX": {
        "up": "VIX (Índice do Medo) em alta, indicando aversão a risco e risco de volatilidade súbita nas bolsas.",
        "down": "VIX em recuo ou patamares baixos, favorecendo ambiente propício para trades técnicos direcionais."
    },
    "GC=F": {
        "up": "Ouro em alta operando como ativo de refúgio global em meio a temores bélicos ou inflacionários.",
        "down": "Ouro em baixa com investidores preferindo alocação em renda variável e títulos soberanos."
    },
    "USDBRL=X": {
        "up": "Pressão de alta no câmbio doméstico com ruído fiscal em Brasília e dólar forte no exterior.",
        "down": "Entrada de fluxo comercial e alívio no risco-país puxam cotação do dólar para baixo."
    }
}

def get_base_prices():
    """Busca os preços de fechamento mais recentes para o cálculo exato de pontos."""
    win_base = 132000.0
    wdo_base = 5450.0
    
    try:
        bvsp_data = yf.Ticker("^BVSP").history(period="3d")
        if not bvsp_data.empty:
            win_base = float(bvsp_data["Close"].iloc[-1])
    except Exception:
        pass
        
    try:
        usd_data = yf.Ticker("USDBRL=X").history(period="3d")
        if not usd_data.empty:
            wdo_base = float(usd_data["Close"].iloc[-1]) * 1000.0
    except Exception:
        pass
        
    return win_base, wdo_base

def enrich_assets_with_catalysts(assets):
    """Adiciona a cada ativo o quanto subiu/desceu e o que influenciou exatamente."""
    enriched = []
    for a in assets:
        sym = a["symbol"]
        chg = a.get("change_pct", 0.0)
        
        tpl = ASSET_CATALYST_TEMPLATES.get(sym, {
            "up": "Movimento comprador acompanhando fluxo internacional de abertura.",
            "down": "Movimento vendedor acompanhando ajuste de posições internacionais."
        })
        
        if chg > 0.05:
            action = f"SUBIU {chg:+.2f}%"
            driver = tpl["up"]
        elif chg < -0.05:
            action = f"CAIU {chg:+.2f}%"
            driver = tpl["down"]
        else:
            action = f"ESTÁVEL ({chg:+.2f}%)"
            driver = "Oscilação lateral em compasso de espera por indicadores econômicos da sessão."

        a_copy = dict(a)
        a_copy["action_badge"] = action
        a_copy["driver"] = driver
        enriched.append(a_copy)
    return enriched

def analyze_with_heuristics(collected_data):
    assets_list = enrich_assets_with_catalysts(collected_data.get("assets", []))
    collected_data["assets"] = assets_list
    assets = {a["symbol"]: a for a in assets_list}
    
    win_base_price, wdo_base_price = get_base_prices()
    
    # Extrair variações
    sp_pct = assets.get("ES=F", {}).get("change_pct", 0.0)
    nasdaq_pct = assets.get("NQ=F", {}).get("change_pct", 0.0)
    dxy_pct = assets.get("DX-Y.NYB", {}).get("change_pct", 0.0)
    tnx_pct = assets.get("^TNX", {}).get("change_pct", 0.0)
    brent_pct = assets.get("BZ=F", {}).get("change_pct", 0.0)
    gas_pct = assets.get("NG=F", {}).get("change_pct", 0.0)
    iron_pct = assets.get("TIO=F", {}).get("change_pct", 0.0)
    china_pct = assets.get("^HSI", {}).get("change_pct", 0.0)
    ewz_pct = assets.get("EWZ", {}).get("change_pct", 0.0)
    vale_adr_pct = assets.get("VALE", {}).get("change_pct", 0.0)
    pbr_adr_pct = assets.get("PBR", {}).get("change_pct", 0.0)
    itub_adr_pct = assets.get("ITUB", {}).get("change_pct", 0.0)
    vix_pct = assets.get("^VIX", {}).get("change_pct", 0.0)
    
    # Ponderação de Elite para o WIN:
    # 1. ADRs em NY (25%): Vale (10%), Petrobras (8%), Itaú (4%), EWZ (3%)
    # 2. Commodities (30%): Minério (15%), Petróleo (10%), Gás (5%)
    # 3. Wall Street (25%): S&P 500 (15%), Nasdaq (10%)
    # 4. China & Ásia (10%)
    # 5. DXY Global (-10%)
    win_score = (
        (vale_adr_pct * 0.10) + (pbr_adr_pct * 0.08) + (itub_adr_pct * 0.04) + (ewz_pct * 0.03) +
        (iron_pct * 0.15) + (brent_pct * 0.10) + (gas_pct * 0.05) + 
        (sp_pct * 0.15) + (nasdaq_pct * 0.10) + 
        (china_pct * 0.10) - 
        (dxy_pct * 0.10)
    )
    
    # Ponderação para o WDO:
    # 1. DXY Global (+30%)
    # 2. Juros Treasuries (+20%)
    # 3. Fluxo de ADRs em NY (-20% - compra de ADR atrai dólar ao país)
    # 4. Commodities (-15% - exportações)
    # 5. Bolsas Mundiais (-15%)
    wdo_score = (
        (dxy_pct * 0.30) + 
        (tnx_pct * 0.20) - 
        (vale_adr_pct * 0.08) - (pbr_adr_pct * 0.07) - (ewz_pct * 0.05) -
        (iron_pct * 0.08) - (brent_pct * 0.07) - 
        (sp_pct * 0.10) - (china_pct * 0.05)
    )
    
    # --- CÁLCULO DE PONTOS & TRAVAS: MINI-ÍNDICE (WIN) ---
    if win_score >= 0.30:
        win_dir = "FORTE ALTA"
        win_trend_badge = "🚀 FORTE TENDÊNCIA DE ALTA"
        p_min = max(0.60, round(win_score * 0.90, 2))
        p_max = round(p_min + 0.80, 2)
        pts_target1 = round(win_base_price * (p_min / 100))
        pts_target2 = round(win_base_price * (p_max / 100))
        price_target1 = round(win_base_price + pts_target1)
        price_target2 = round(win_base_price + pts_target2)
        pts_trava = round(win_base_price * -0.003)
        price_trava = round(win_base_price + pts_trava)
        win_exp_range = f"+{p_min:.1f}% a +{p_max:.1f}%"
        win_points_range = f"+{pts_target1:,} a +{pts_target2:,} pts".replace(",", ".")
        win_reason = f"Confluência altista massiva: Minério ({iron_pct:+.2f}%), ADR Vale ({vale_adr_pct:+.2f}%) e Wall Street em alta acelerada."
    elif win_score > 0.10:
        win_dir = "ALTA"
        win_trend_badge = "▲ TENDÊNCIA DE ALTA"
        p_min = max(0.40, round(win_score * 0.85, 2))
        p_max = round(p_min + 0.60, 2)
        pts_target1 = round(win_base_price * (p_min / 100))
        pts_target2 = round(win_base_price * (p_max / 100))
        price_target1 = round(win_base_price + pts_target1)
        price_target2 = round(win_base_price + pts_target2)
        pts_trava = round(win_base_price * -0.0035)
        price_trava = round(win_base_price + pts_trava)
        win_exp_range = f"+{p_min:.1f}% a +{p_max:.1f}%"
        win_points_range = f"+{pts_target1:,} a +{pts_target2:,} pts".replace(",", ".")
        win_reason = f"Impulso comprador internacional liderado por Minério ({iron_pct:+.2f}%), Petróleo ({brent_pct:+.2f}%) e bolsas de NY ({sp_pct:+.2f}%)."
    elif win_score <= -0.30:
        win_dir = "FORTE BAIXA"
        win_trend_badge = "🔻 FORTE TENDÊNCIA DE BAIXA"
        p_min = min(-0.60, round(win_score * 0.90, 2))
        p_max = round(p_min - 0.80, 2)
        pts_target1 = round(win_base_price * (p_min / 100))
        pts_target2 = round(win_base_price * (p_max / 100))
        price_target1 = round(win_base_price + pts_target1)
        price_target2 = round(win_base_price + pts_target2)
        pts_trava = round(win_base_price * 0.003)
        price_trava = round(win_base_price + pts_trava)
        win_exp_range = f"{p_max:.1f}% a {p_min:.1f}%"
        win_points_range = f"{pts_target2:,} a {pts_target1:,} pts".replace(",", ".")
        win_reason = f"Forte aversão a risco global com queda severa em NY ({sp_pct:+.2f}%) e liquidação em emergentes."
    elif win_score < -0.10:
        win_dir = "BAIXA"
        win_trend_badge = "▼ TENDÊNCIA DE BAIXA"
        p_min = min(-0.40, round(win_score * 0.85, 2))
        p_max = round(p_min - 0.60, 2)
        pts_target1 = round(win_base_price * (p_min / 100))
        pts_target2 = round(win_base_price * (p_max / 100))
        price_target1 = round(win_base_price + pts_target1)
        price_target2 = round(win_base_price + pts_target2)
        pts_trava = round(win_base_price * 0.0035)
        price_trava = round(win_base_price + pts_trava)
        win_exp_range = f"{p_max:.1f}% a {p_min:.1f}%"
        win_points_range = f"{pts_target2:,} a {pts_target1:,} pts".replace(",", ".")
        win_reason = f"Pressão de baixa externa provocada por retração em Wall Street ({sp_pct:+.2f}%) e fraqueza em commodities."
    else:
        win_dir = "LATERAL"
        win_trend_badge = "◆ LATERAL / CONSOLIDAÇÃO"
        p_min = -0.30
        p_max = 0.30
        win_exp_range = "-0.3% a +0.3%"
        pts_target1 = round(win_base_price * 0.003)
        pts_target2 = round(win_base_price * -0.003)
        price_target1 = round(win_base_price + pts_target1)
        price_target2 = round(win_base_price + pts_target2)
        pts_trava = round(win_base_price * -0.005)
        price_trava = round(win_base_price + pts_trava)
        win_points_range = f"{pts_target2:,} a +{pts_target1:,} pts".replace(",", ".")
        win_reason = "Variações mistas entre commodities e bolsas na madrugada; abertura sem tendência direcional forte."

    # --- CÁLCULO DE PONTOS & TRAVAS: MINI-DÓLAR (WDO) ---
    if wdo_score >= 0.25:
        wdo_dir = "FORTE ALTA"
        wdo_trend_badge = "🚀 FORTE TENDÊNCIA DE ALTA"
        d_min = max(0.50, round(wdo_score * 0.85, 2))
        d_max = round(d_min + 0.60, 2)
        pts_wdo_target1 = round(wdo_base_price * (d_min / 100), 1)
        pts_wdo_target2 = round(wdo_base_price * (d_max / 100), 1)
        price_wdo_target1 = round(wdo_base_price + pts_wdo_target1, 1)
        price_wdo_target2 = round(wdo_base_price + pts_wdo_target2, 1)
        pts_wdo_trava = round(wdo_base_price * -0.003, 1)
        price_wdo_trava = round(wdo_base_price + pts_wdo_trava, 1)
        wdo_exp_range = f"+{d_min:.1f}% a +{d_max:.1f}%"
        wdo_points_range = f"+{pts_wdo_target1:.1f} a +{pts_wdo_target2:.1f} pts"
        wdo_reason = f"Forte corrida para o dólar: DXY disparando ({dxy_pct:+.2f}%) e juros dos Treasuries em alta acentuada."
    elif wdo_score > 0.08:
        wdo_dir = "ALTA"
        wdo_trend_badge = "▲ TENDÊNCIA DE ALTA"
        d_min = max(0.30, round(wdo_score * 0.70, 2))
        d_max = round(d_min + 0.50, 2)
        pts_wdo_target1 = round(wdo_base_price * (d_min / 100), 1)
        pts_wdo_target2 = round(wdo_base_price * (d_max / 100), 1)
        price_wdo_target1 = round(wdo_base_price + pts_wdo_target1, 1)
        price_wdo_target2 = round(wdo_base_price + pts_wdo_target2, 1)
        pts_wdo_trava = round(wdo_base_price * -0.0035, 1)
        price_wdo_trava = round(wdo_base_price + pts_wdo_trava, 1)
        wdo_exp_range = f"+{d_min:.1f}% a +{d_max:.1f}%"
        wdo_points_range = f"+{pts_wdo_target1:.1f} a +{pts_wdo_target2:.1f} pts"
        wdo_reason = f"Dólar internacional fortalecido (DXY: {dxy_pct:+.2f}%) e juros dos Treasuries pressionando moedas emergentes."
    elif wdo_score <= -0.25:
        wdo_dir = "FORTE BAIXA"
        wdo_trend_badge = "🔻 FORTE TENDÊNCIA DE BAIXA"
        d_min = min(-0.50, round(wdo_score * 0.85, 2))
        d_max = round(d_min - 0.60, 2)
        pts_wdo_target1 = round(wdo_base_price * (d_min / 100), 1)
        pts_wdo_target2 = round(wdo_base_price * (d_max / 100), 1)
        price_wdo_target1 = round(wdo_base_price + pts_wdo_target1, 1)
        price_wdo_target2 = round(wdo_base_price + pts_wdo_target2, 1)
        pts_wdo_trava = round(wdo_base_price * 0.003, 1)
        price_wdo_trava = round(wdo_base_price + pts_wdo_trava, 1)
        wdo_exp_range = f"{d_max:.1f}% a {d_min:.1f}%"
        wdo_points_range = f"{pts_wdo_target2:.1f} a {pts_wdo_target1:.1f} pts"
        wdo_reason = f"Forte desvalorização global da moeda americana e entrada massiva de fluxo em commodities e emergentes."
    elif wdo_score < -0.08:
        wdo_dir = "BAIXA"
        wdo_trend_badge = "▼ TENDÊNCIA DE BAIXA"
        d_min = min(-0.30, round(wdo_score * 0.70, 2))
        d_max = round(d_min - 0.50, 2)
        pts_wdo_target1 = round(wdo_base_price * (d_min / 100), 1)
        pts_wdo_target2 = round(wdo_base_price * (d_max / 100), 1)
        price_wdo_target1 = round(wdo_base_price + pts_wdo_target1, 1)
        price_wdo_target2 = round(wdo_base_price + pts_wdo_target2, 1)
        pts_wdo_trava = round(wdo_base_price * 0.0035, 1)
        price_wdo_trava = round(wdo_base_price + pts_wdo_trava, 1)
        wdo_exp_range = f"{d_max:.1f}% a {d_min:.1f}%"
        wdo_points_range = f"{pts_wdo_target2:.1f} a {pts_wdo_target1:.1f} pts"
        wdo_reason = f"Arrefecimento do Dólar global (DXY: {dxy_pct:+.2f}%) e alta de commodities favorecem entrada de divisas."
    else:
        wdo_dir = "LATERAL"
        wdo_trend_badge = "◆ LATERAL / CONSOLIDAÇÃO"
        d_min = -0.20
        d_max = 0.20
        wdo_exp_range = "-0.2% a +0.2%"
        pts_wdo_target1 = round(wdo_base_price * -0.002, 1)
        pts_wdo_target2 = round(wdo_base_price * 0.002, 1)
        price_wdo_target1 = round(wdo_base_price + pts_wdo_target1, 1)
        price_wdo_target2 = round(wdo_base_price + pts_wdo_target2, 1)
        pts_wdo_trava = round(wdo_base_price * 0.004, 1)
        price_wdo_trava = round(wdo_base_price + pts_wdo_trava, 1)
        wdo_points_range = f"{pts_wdo_target1:.1f} a +{pts_wdo_target2:.1f} pts"
        wdo_reason = "Mercado cambial em equilíbrio na abertura, aguardando agenda do dia e fluxo institucional."

    # Humor do mercado
    # Humor e Estresse do Mercado (Score 1 a 10)
    if win_score > 0.1 and wdo_score < 0:
        sentiment = "RISK-ON (Apetite a Risco Global)"
        risk_score = 3
        risk_label = "Mercado Técnico & Direcional (Baixo Estresse)"
        risk_color = "emerald"
    elif win_score < -0.1 and wdo_score > 0:
        sentiment = "RISK-OFF (Aversão a Risco / Defensivo)"
        risk_score = 7
        risk_label = "Aversão a Risco Elevada (Cuidado com Stops)"
        risk_color = "rose"
    else:
        sentiment = "NEUTRO / EQUILIBRADO"
        risk_score = 5
        risk_label = "Mercado Misto / Ruído Moderado"
        risk_color = "amber"

    # Plano de Voo em 30 Segundos (O que fazer na abertura)
    if win_dir == "ALTA":
        win_flight = f"Comprador com suporte nos {price_trava:,.0f} pts. Buscar 1º Take em {price_target1:,.0f} pts e expansão em {price_target2:,.0f} pts.".replace(",", ".")
    elif win_dir == "BAIXA":
        win_flight = f"Vendedor com resistência nos {price_trava:,.0f} pts. Buscar 1º Take em {price_target1:,.0f} pts e expansão em {price_target2:,.0f} pts.".replace(",", ".")
    else:
        win_flight = f"Consolidação inicial ({win_exp_range}). Aguardar definição entre {price_target1:,.0f} e {price_target2:,.0f} pts. Trava em {price_trava:,.0f} pts.".replace(",", ".")

    if wdo_dir == "ALTA":
        wdo_flight = f"Comprador acompanhando força externa. Buscar alvo em {price_wdo_target1:,.1f} pts. Trava de stop nos {price_wdo_trava:,.1f} pts.".replace(",", ".")
    elif wdo_dir == "BAIXA":
        wdo_flight = f"Vendedor acompanhando recuo do Forex. Buscar 1º alvo em {price_wdo_target1:,.1f} pts e expansão em {price_wdo_target2:,.1f} pts. Trava de stop nos {price_wdo_trava:,.1f} pts.".replace(",", ".")
    else:
        wdo_flight = f"Câmbio equilibrado ({wdo_exp_range}). Suporte em {price_wdo_target1:,.1f} pts e resistência em {price_wdo_target2:,.1f} pts. Trava em {price_wdo_trava:,.1f} pts.".replace(",", ".")

    danger_zone = "Atenção máxima às 10:00 (Abertura do Mercado à Vista B3) e 10:30 (Abertura de Wall Street). Evite ordens a mercado durante o leilão."

    return {
        "market_sentiment": sentiment,
        "risk_score": risk_score,
        "risk_label": risk_label,
        "risk_color": risk_color,
        "flight_plan": {
            "win": win_flight,
            "wdo": wdo_flight,
            "danger": danger_zone
        },
        "win": {
            "direction": win_dir,
            "trend_badge": win_trend_badge,
            "expected_range": win_exp_range,
            "points_range": win_points_range,
            "base_price": f"{win_base_price:,.0f} pts".replace(",", "."),
            "target_1_label": f"🎯 Alvo 1 ({p_min:+.1f}%):",
            "target_1_val": f"{price_target1:,.0f} pts ({pts_target1:+d} pts)".replace(",", "."),
            "target_2_label": f"🎯 Alvo 2 ({p_max:+.1f}%):",
            "target_2_val": f"{price_target2:,.0f} pts ({pts_target2:+d} pts)".replace(",", "."),
            "trava_label": "🛡️ Trava de Stop:",
            "trava_val": f"{price_trava:,.0f} pts ({pts_trava:+d} pts)".replace(",", "."),
            "target_1": f"{price_target1:,.0f} pts ({pts_target1:+d} pts)".replace(",", "."),
            "target_2": f"{price_target2:,.0f} pts ({pts_target2:+d} pts)".replace(",", "."),
            "trava_risco": f"{price_trava:,.0f} pts ({pts_trava:+d} pts)".replace(",", "."),
            "catalyst": win_reason
        },
        "wdo": {
            "direction": wdo_dir,
            "trend_badge": wdo_trend_badge,
            "expected_range": wdo_exp_range,
            "points_range": wdo_points_range,
            "base_price": f"{wdo_base_price:,.1f} pts".replace(",", "."),
            "target_1_label": f"🎯 Alvo 1 ({d_min:+.1f}%):",
            "target_1_val": f"{price_wdo_target1:,.1f} pts ({pts_wdo_target1:+.1f} pts)".replace(",", "."),
            "target_2_label": f"🎯 Alvo 2 ({d_max:+.1f}%):",
            "target_2_val": f"{price_wdo_target2:,.1f} pts ({pts_wdo_target2:+.1f} pts)".replace(",", "."),
            "trava_label": "🛡️ Trava de Stop:",
            "trava_val": f"{price_wdo_trava:,.1f} pts ({pts_wdo_trava:+.1f} pts)".replace(",", "."),
            "target_1": f"{price_wdo_target1:,.1f} pts ({pts_wdo_target1:+.1f} pts)".replace(",", "."),
            "target_2": f"{price_wdo_target2:,.1f} pts ({pts_wdo_target2:+.1f} pts)".replace(",", "."),
            "trava_risco": f"{price_wdo_trava:,.1f} pts ({pts_wdo_trava:+.1f} pts)".replace(",", "."),
            "catalyst": wdo_reason
        },
        "overnight_summary": [
            f"Wall Street: S&P Futuro em {sp_pct:+.2f}% e Nasdaq em {nasdaq_pct:+.2f}%.",
            f"Commodities: Minério de ferro cotado a ${assets.get('TIO=F', {}).get('price', 'N/D')} ({iron_pct:+.2f}%), Petróleo Brent a ${assets.get('BZ=F', {}).get('price', 'N/D')} ({brent_pct:+.2f}%) e Gás Natural a ${assets.get('NG=F', {}).get('price', 'N/D')}.",
            f"Câmbio & Juros: DXY em {assets.get('DX-Y.NYB', {}).get('price', 'N/D')} ({dxy_pct:+.2f}%) e Treasury 10A em {tnx_pct:+.2f}%."
        ]
    }

def analyze_with_gemini(collected_data, api_key):
    """Análise do Gemini enriquecida com os cálculos exatos de pontos."""
    # Gera a base quantitativa de pontos para garantir exatidão matemática
    base_res = analyze_with_heuristics(collected_data)
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
Você é um estrategista macro sênior de mesa proprietária de Day Trade na B3 (Brasil).
Analise os ativos internacionais e as notícias das últimas 4h e 24h.

DADOS DE MERCADO COM PONTOS E CATALISADORES:
{json.dumps(base_res, ensure_ascii=False, indent=2)}

NOTÍCIAS RECENTES:
{json.dumps(collected_data['news'], ensure_ascii=False, indent=2)}

Refine o parecer mantendo a mesma estrutura JSON exata, melhorando os catalisadores para explicar com clareza o que influenciou os mercados de petróleo, gás, minério, EUA e China.
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        gemini_json = json.loads(text)
        # Garantir integridade dos números de pontos calculados
        gemini_json["win"]["base_price"] = base_res["win"]["base_price"]
        gemini_json["win"]["points_range"] = base_res["win"]["points_range"]
        gemini_json["win"]["target_1"] = base_res["win"]["target_1"]
        gemini_json["win"]["target_2"] = base_res["win"]["target_2"]
        gemini_json["win"]["trava_risco"] = base_res["win"]["trava_risco"]
        
        gemini_json["wdo"]["base_price"] = base_res["wdo"]["base_price"]
        gemini_json["wdo"]["points_range"] = base_res["wdo"]["points_range"]
        gemini_json["wdo"]["target_1"] = base_res["wdo"]["target_1"]
        gemini_json["wdo"]["target_2"] = base_res["wdo"]["target_2"]
        gemini_json["wdo"]["trava_risco"] = base_res["wdo"]["trava_risco"]
        return gemini_json
    except Exception as e:
        print(f"Aviso Gemini: {e}. Usando motor quantitativo calibrado.")
        return base_res

def analyze(collected_data):
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and len(api_key.strip()) > 5:
        return analyze_with_gemini(collected_data, api_key)
    return analyze_with_heuristics(collected_data)

if __name__ == "__main__":
    from collector import collect_all
    print("Testando motor com pontos e travas...")
    d = collect_all()
    res = analyze(d)
    print("WIN Alvo 1:", res["win"]["target_1"])
    print("WIN Trava:", res["win"]["trava_risco"])
    print("WDO Alvo 1:", res["wdo"]["target_1"])
    print("WDO Trava:", res["wdo"]["trava_risco"])
