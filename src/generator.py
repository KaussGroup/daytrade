# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

def render_html_dashboard(analysis, collected_data, accuracy_metrics, output_path="index.html"):
    """Renderiza um dashboard financeiro ultra-fluido, simples e objetivo."""
    
    today_str = datetime.now().strftime("%d/%m/%Y")
    update_time = datetime.now().strftime("%H:%M")
    
    win = analysis["win"]
    wdo = analysis["wdo"]
    
    # Cores e classes do WIN
    win_dir = win["direction"]
    if "FORTE ALTA" in win_dir:
        win_badge_class = "bg-emerald-500/30 text-emerald-300 border-emerald-400 font-black shadow-lg shadow-emerald-500/20"
        win_text_color = "text-emerald-400"
        win_icon = "🚀"
    elif "ALTA" in win_dir:
        win_badge_class = "bg-emerald-500/20 text-emerald-400 border-emerald-500/40 font-bold"
        win_text_color = "text-emerald-400"
        win_icon = "▲"
    elif "FORTE BAIXA" in win_dir:
        win_badge_class = "bg-rose-500/30 text-rose-300 border-rose-400 font-black shadow-lg shadow-rose-500/20"
        win_text_color = "text-rose-400"
        win_icon = "🔻"
    elif "BAIXA" in win_dir:
        win_badge_class = "bg-rose-500/20 text-rose-400 border-rose-500/40 font-bold"
        win_text_color = "text-rose-400"
        win_icon = "▼"
    else:
        win_badge_class = "bg-slate-800 text-slate-300 border-slate-700 font-bold"
        win_text_color = "text-slate-300"
        win_icon = "◆"

    # Cores e classes do WDO
    wdo_dir = wdo["direction"]
    if "FORTE ALTA" in wdo_dir:
        wdo_badge_class = "bg-emerald-500/30 text-emerald-300 border-emerald-400 font-black shadow-lg shadow-emerald-500/20"
        wdo_text_color = "text-emerald-400"
        wdo_icon = "🚀"
    elif "ALTA" in wdo_dir:
        wdo_badge_class = "bg-emerald-500/20 text-emerald-400 border-emerald-500/40 font-bold"
        wdo_text_color = "text-emerald-400"
        wdo_icon = "▲"
    elif "FORTE BAIXA" in wdo_dir:
        wdo_badge_class = "bg-rose-500/30 text-rose-300 border-rose-400 font-black shadow-lg shadow-rose-500/20"
        wdo_text_color = "text-rose-400"
        wdo_icon = "🔻"
    elif "BAIXA" in wdo_dir:
        wdo_badge_class = "bg-rose-500/20 text-rose-400 border-rose-500/40 font-bold"
        wdo_text_color = "text-rose-400"
        wdo_icon = "▼"
    else:
        wdo_badge_class = "bg-slate-800 text-slate-300 border-slate-700 font-bold"
        wdo_text_color = "text-slate-300"
        wdo_icon = "◆"

    # Plano de Voo e Risco
    fp = analysis.get("flight_plan", {
        "win": f"Viés {win_dir}: Alvo 1 em {win.get('target_1')} e Trava em {win.get('trava_risco')}.",
        "wdo": f"Viés {wdo_dir}: Alvo 1 em {wdo.get('target_1')} e Trava em {wdo.get('trava_risco')}.",
        "danger": "Atenção máxima às 10:00 (Abertura B3) e 10:30 (Wall Street)."
    })
    risk_score = analysis.get("risk_score", 5)
    risk_label = analysis.get("risk_label", "Mercado Misto / Ruído Moderado")
    
    # Formatador dinâmico de cores dos alvos (Verde para subida/positivo, Vermelho para queda/negativo)
    def format_target_row(label, val_str, is_stop=False):
        if not val_str:
            return f'<span class="font-sans font-semibold text-slate-400">{label}</span><span class="font-bold text-slate-400">N/D</span>'
        
        if is_stop:
            badge_cls = "text-rose-400 bg-rose-500/10 px-2.5 py-0.5 rounded-lg border border-rose-500/30 font-bold"
        else:
            # Subida (+ pts ou +%) -> VERDE
            if "(+" in val_str or "+ " in val_str or "pts (+" in val_str:
                badge_cls = "text-emerald-400 bg-emerald-500/15 px-2.5 py-0.5 rounded-lg border border-emerald-500/30 font-bold"
            # Queda (- pts ou -%) -> VERMELHO
            elif "(-" in val_str or "- " in val_str or "pts (-" in val_str:
                badge_cls = "text-rose-400 bg-rose-500/15 px-2.5 py-0.5 rounded-lg border border-rose-500/30 font-bold"
            else:
                badge_cls = "text-amber-400 bg-amber-500/10 px-2.5 py-0.5 rounded-lg border border-amber-500/20 font-bold"
                
        return f'<span class="font-sans font-semibold text-slate-300">{label}</span><span class="font-mono {badge_cls}">{val_str}</span>'

    win_t1_html = format_target_row(win.get('target_1_label', '🎯 Alvo 1:'), win.get('target_1_val', win.get('target_1')))
    win_t2_html = format_target_row(win.get('target_2_label', '🎯 Alvo 2:'), win.get('target_2_val', win.get('target_2')))
    win_trava_html = format_target_row(win.get('trava_label', '🛡️ Trava de Stop:'), win.get('trava_val', win.get('trava_risco')), is_stop=True)

    wdo_t1_html = format_target_row(wdo.get('target_1_label', '🎯 Alvo 1:'), wdo.get('target_1_val', wdo.get('target_1')))
    wdo_t2_html = format_target_row(wdo.get('target_2_label', '🎯 Alvo 2:'), wdo.get('target_2_val', wdo.get('target_2')))
    wdo_trava_html = format_target_row(wdo.get('trava_label', '🛡️ Trava de Stop:'), wdo.get('trava_val', wdo.get('trava_risco')), is_stop=True)

    # Coleta de preços base para comparação em Tempo Real
    btc_asset = next((a for a in collected_data.get("assets", []) if a["symbol"] == "BTC-USD"), {})
    btc_asset_price = btc_asset.get("price", "N/D")
    
    eur_asset = next((a for a in collected_data.get("assets", []) if a["symbol"] == "EURUSD=X"), {})
    eur_price = eur_asset.get("price", "N/D")

    sp_asset = next((a for a in collected_data.get("assets", []) if a["symbol"] == "ES=F"), {})
    sp_price = sp_asset.get("price", "N/D")

    nq_asset = next((a for a in collected_data.get("assets", []) if a["symbol"] == "NQ=F"), {})
    nq_price = nq_asset.get("price", "N/D")

    # Barra visual de 10 níveis de risco
    risk_bars_html = ""
    for i in range(1, 11):
        if i <= risk_score:
            c = "bg-emerald-500" if i <= 3 else ("bg-amber-500" if i <= 6 else "bg-rose-500")
        else:
            c = "bg-slate-800"
        risk_bars_html += f'<div class="h-2 flex-1 rounded-full {c}"></div>'

    # Separar ativos por grupos de análise
    adrs_html = ""
    commodities_html = ""
    forex_crypto_html = ""
    macro_html = ""
    
    for a in collected_data.get("assets", []):
        chg = a.get("change_pct", 0.0)
        c_class = "text-emerald-400" if chg > 0 else ("text-rose-400" if chg < 0 else "text-gray-400")
        badge_bg = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" if chg > 0 else ("bg-rose-500/10 text-rose-400 border-rose-500/30" if chg < 0 else "bg-slate-800 text-slate-400 border-slate-700")
        action_text = a.get("action_badge", a.get("change_str", "0.00%"))
        driver_text = a.get("driver", "Acompanhando fluxo de abertura dos mercados internacionais.")
        cat = a.get("category", "")
        
        card = f"""
        <div class="bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition rounded-xl p-3.5 flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between text-xs mb-1.5">
                    <span class="font-bold text-slate-200 flex items-center gap-1.5">{a['icon']} {a['name']}</span>
                    <span class="text-[10px] px-1.5 py-0.5 rounded border font-semibold {badge_bg}">{action_text}</span>
                </div>
                <div class="flex items-baseline justify-between mb-2">
                    <span class="text-base font-black text-slate-100 font-mono">{a['price']}</span>
                    <span class="text-xs font-bold font-mono {c_class}">{a['change_str']}</span>
                </div>
            </div>
            <div class="border-t border-slate-800/80 pt-2 mt-1">
                <p class="text-[11px] text-slate-400 leading-relaxed"><span class="text-amber-400/90 font-medium">Motivo:</span> {driver_text}</p>
            </div>
        </div>
        """
        
        if "Pré-Mercado" in cat:
            adrs_html += card
        elif "Commodities" in cat:
            commodities_html += card
        elif "Crypto" in cat or "Forex" in cat:
            forex_crypto_html += card
        else:
            macro_html += card

    # Status Direcional do Dólar no Pré-Mercado
    usd_asset = next((a for a in collected_data.get("assets", []) if a["symbol"] == "USDBRL=X"), {})
    usd_chg = usd_asset.get("change_pct", 0.0)
    usd_price = usd_asset.get("price", "N/D")
    
    if usd_chg > 0.05:
        dollar_premarket_badge = f"▲ DÓLAR SUBINDO NO PRÉ-MERCADO ({usd_chg:+.2f}%)"
        dollar_premarket_style = "bg-rose-500/20 text-rose-400 border-rose-500/40"
        dollar_premarket_desc = f"Paridade USD/BRL negociada a R$ {usd_price} no Forex com pressão compradora, indicando possível abertura de gap de alta no WDO."
    elif usd_chg < -0.05:
        dollar_premarket_badge = f"▼ DÓLAR CAINDO NO PRÉ-MERCADO ({usd_chg:+.2f}%)"
        dollar_premarket_style = "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
        dollar_premarket_desc = f"Paridade USD/BRL negociada a R$ {usd_price} no Forex em recuo, favorecendo abertura com gap de baixa no WDO."
    else:
        dollar_premarket_badge = f"◆ DÓLAR ESTÁVEL NO PRÉ-MERCADO ({usd_chg:+.2f}%)"
        dollar_premarket_style = "bg-slate-800 text-slate-300 border-slate-700"
        dollar_premarket_desc = f"Cotação a R$ {usd_price} sem pressão de gap acentuada; abertura próxima ao ajuste anterior."

    # Indicadores do Mercado de Trabalho em HTML
    labor_html = ""
    for lb in collected_data.get("labor_indicators", []):
        impact_badge = "bg-rose-500/20 text-rose-400 border-rose-500/30" if lb["impact"] == "MÁXIMO" else "bg-amber-500/20 text-amber-400 border-amber-500/30"
        labor_html += f"""
        <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between mb-1.5">
                    <span class="text-xs font-bold text-slate-100">{lb['name']}</span>
                    <span class="text-[10px] px-1.5 py-0.5 rounded border uppercase font-bold {impact_badge}">{lb['impact']}</span>
                </div>
                <div class="text-[11px] text-amber-400/90 font-mono mb-2">
                    <span>{lb['country']} | {lb['frequency']}</span>
                </div>
            </div>
            <div class="border-t border-slate-800/80 pt-2">
                <p class="text-[11px] text-slate-400 leading-relaxed"><strong class="text-slate-300">Gatilho de Trade:</strong> {lb['rule']}</p>
            </div>
        </div>
        """

    # Categorias de notícias em HTML
    news_sections = ""
    for key, topic in collected_data.get("news", {}).items():
        items_html = ""
        for n in topic.get("items", []):
            items_html += f"""
            <a href="{n['link']}" target="_blank" class="block p-2.5 rounded-lg bg-slate-900/50 hover:bg-slate-800/80 border border-slate-800/60 transition group">
                <p class="text-xs text-slate-200 group-hover:text-amber-400 transition font-medium line-clamp-2 leading-relaxed">{n['title']}</p>
                <div class="flex items-center justify-between mt-1.5 text-[10px] text-slate-400">
                    <span class="font-semibold text-slate-400">{n['source']}</span>
                    <span>{n['published'][:16] if n.get('published') else ''}</span>
                </div>
            </a>
            """
        if not items_html:
            items_html = "<p class='text-xs text-slate-500 italic p-2'>Sem notícias críticas registradas neste tópico nas últimas horas.</p>"
            
        news_sections += f"""
        <div class="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center justify-between">
                <span>{topic['title']}</span>
            </h3>
            <div class="space-y-2">
                {items_html}
            </div>
        </div>
        """

    # Calendário em HTML
    calendar_html = ""
    for c in collected_data.get("calendar", []):
        badge = "bg-rose-500/20 text-rose-400 border-rose-500/30" if c["impact"] == "MÁXIMO" else ("bg-amber-500/20 text-amber-400 border-amber-500/30" if c["impact"] == "ALTO" else "bg-slate-800 text-slate-300 border-slate-700")
        calendar_html += f"""
        <div class="flex items-start gap-3 p-2.5 bg-slate-900/50 border border-slate-800/60 rounded-lg">
            <span class="px-2 py-0.5 text-xs font-mono font-bold text-amber-400 bg-amber-400/10 rounded border border-amber-400/20">{c['time']}</span>
            <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                    <span class="text-xs font-semibold text-slate-200">{c['event']}</span>
                    <span class="text-[9px] px-1.5 py-0.2 rounded border uppercase font-bold {badge}">{c['impact']}</span>
                </div>
                <p class="text-[11px] text-slate-400 mt-0.5">{c['note']}</p>
            </div>
        </div>
        """

    # Tabela de assertividade recente (Auditada em 3 níveis: Alvo 1, Alvo 2 e Faixa de Variação)
    history_rows = ""
    for h in accuracy_metrics.get("recent_records", [])[:15]:
        w = h.get("wdo", {})
        t1_badge = "<span class='text-emerald-400 font-bold'>✔ Atingiu</span>" if w.get("t1_hit") else "<span class='text-slate-500'>-</span>"
        t2_badge = "<span class='text-emerald-400 font-bold'>✔ Atingiu</span>" if w.get("t2_hit") else "<span class='text-slate-500'>-</span>"
        range_badge = "<span class='text-emerald-400 font-bold'>✔ Na Faixa</span>" if w.get("range_hit") else "<span class='text-rose-400 font-bold'>✖ Fora</span>"
        
        bias_style = "text-rose-400" if w.get("bias") == "BAIXA" else ("text-emerald-400" if w.get("bias") == "ALTA" else "text-amber-400")
        
        history_rows += f"""
        <tr class="border-b border-slate-800/60 hover:bg-slate-800/30 text-xs">
            <td class="py-2.5 px-3 font-mono text-slate-300">{h['date']}</td>
            <td class="py-2.5 px-3 font-bold {bias_style}">{w.get('bias', '-')}</td>
            <td class="py-2.5 px-3">{t1_badge}</td>
            <td class="py-2.5 px-3">{t2_badge}</td>
            <td class="py-2.5 px-3 font-mono text-slate-300">{w.get('expected_pct', '-')}</td>
            <td class="py-2.5 px-3 font-mono font-semibold">{w.get('actual_pct', '-')}</td>
            <td class="py-2.5 px-3">{range_badge}</td>
        </tr>
        """

    records_json = json.dumps(accuracy_metrics.get("recent_records", []), ensure_ascii=False)
    today_wdo_json = json.dumps(wdo, ensure_ascii=False)
    today_iso_date = datetime.now().strftime("%Y-%m-%d")

    html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar Day Trade B3 - {today_str}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #070a10;
            color: #f1f5f9;
        }}
        .font-mono {{
            font-family: 'JetBrains Mono', monospace;
        }}
    </style>
</head>
<body class="min-h-screen antialiased selection:bg-amber-500/30 selection:text-amber-300 pb-12">
    
    <!-- Lock Screen Modal (Autenticação por E-mail + Senha) -->
    <div id="authLockModal" class="fixed inset-0 z-50 bg-slate-950/95 backdrop-blur-md flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-700/80 rounded-2xl p-6 sm:p-8 max-w-sm w-full text-center shadow-2xl space-y-4">
            <div class="w-14 h-14 mx-auto rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-2xl shadow-inner">
                🔐
            </div>
            <div>
                <h3 class="text-lg font-bold text-white tracking-tight">Radar Kauss Day Trade</h3>
                <p class="text-xs text-slate-400 mt-1">Acesso Restrito — Operador Autorizado</p>
            </div>
            <div class="space-y-3 pt-1">
                <div class="text-left">
                    <label class="text-[11px] font-medium text-slate-400 block mb-1">E-mail Cadastrado:</label>
                    <input type="email" id="authEmailInput" placeholder="adm.grupokauss@gmail.com" 
                        autocomplete="email" autocorrect="off" autocapitalize="off" spellcheck="false"
                        class="w-full text-sm font-medium bg-slate-950 border border-slate-700 rounded-xl py-2.5 px-3.5 text-white focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400 transition-all placeholder:text-slate-600">
                </div>
                
                <div class="text-left">
                    <label class="text-[11px] font-medium text-slate-400 block mb-1">Senha de Acesso:</label>
                    <input type="password" id="authPasswordInput" placeholder="••••••••••••" 
                        autocomplete="current-password"
                        class="w-full text-sm font-medium bg-slate-950 border border-slate-700 rounded-xl py-2.5 px-3.5 text-white focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400 transition-all placeholder:text-slate-600">
                </div>

                <p id="authErrorMsg" class="text-rose-400 text-xs font-semibold hidden text-center">E-mail ou senha incorretos.</p>
                
                <div class="flex items-center justify-between text-xs text-slate-400 pt-1">
                    <label class="flex items-center gap-2 cursor-pointer select-none">
                        <input type="checkbox" id="rememberEmail" checked class="rounded bg-slate-950 border-slate-700 text-amber-500 focus:ring-0">
                        <span>Lembrar neste aparelho</span>
                    </label>
                    <span class="text-[10px] text-emerald-400 font-mono">256-bit SSL</span>
                </div>

                <button onclick="handleEmailLogin()" class="w-full py-3 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-yellow-300 text-slate-950 font-black rounded-xl text-sm transition-all shadow-lg shadow-amber-500/20 active:scale-95 cursor-pointer mt-1">
                    Entrar no Painel 🔓
                </button>
            </div>
        </div>
    </div>
    
    <!-- Top Bar -->
    <header class="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-yellow-300 flex items-center justify-center font-black text-slate-950 text-sm shadow-lg shadow-amber-500/20">
                    B3
                </div>
                <div>
                    <h1 class="text-sm font-extrabold tracking-tight text-white flex items-center gap-2">
                        RADAR DE ABERTURA DAY TRADE
                        <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                            AO VIVO
                        </span>
                    </h1>
                    <p class="text-[11px] text-slate-400">Projeção em Pontos | Travas de Stop | Pré-Mercado NY</p>
                </div>
            </div>
            
            <div class="flex items-center gap-4 text-xs">
                <div id="userAuthBadge" class="hidden sm:flex items-center gap-1.5 bg-slate-900/80 px-2.5 py-1 rounded-lg border border-slate-800 text-[11px] text-slate-400">
                    <span>👤</span>
                    <span id="userEmailSpan" class="text-slate-300 font-medium font-mono"></span>
                    <button onclick="logoutEmail()" class="text-slate-500 hover:text-rose-400 text-[10px] ml-1" title="Sair deste dispositivo">(sair)</button>
                </div>
                <div class="text-right">
                    <p class="text-slate-400 text-[10px]">Data do Pregão</p>
                    <p class="font-mono font-bold text-slate-200">{today_str} | {update_time} BRT</p>
                </div>
                <div class="h-6 w-px bg-slate-800"></div>
                <div class="text-right">
                    <p class="text-slate-400 text-[10px]">Humor Global</p>
                    <span class="font-bold text-amber-400">{analysis['market_sentiment']}</span>
                </div>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 py-5 space-y-5">

        <!-- 1. HERO: PLANO DE VOO EM 30 SEGUNDOS -->
        <section class="bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 border-2 border-amber-500/40 rounded-2xl p-4 sm:p-5 shadow-2xl relative overflow-hidden">
            <div class="flex flex-wrap items-center justify-between gap-3 mb-3.5 pb-2.5 border-b border-slate-800">
                <div class="flex items-center gap-2">
                    <span class="w-6 h-6 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-black">⚡</span>
                    <h2 class="text-xs font-black uppercase tracking-wider text-amber-400">
                        Plano de Voo em 30 Segundos (Resumo Executivo)
                    </h2>
                </div>
                <button id="copyBtn" onclick="copyTradePlan()" class="px-3.5 py-1.5 rounded-xl bg-blue-600/30 hover:bg-blue-600/50 border border-blue-500/40 text-xs font-bold text-blue-200 transition flex items-center gap-1.5 shadow-md active:scale-95">
                    📋 Copiar Níveis do Dólar (WDO)
                </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                <div class="bg-slate-950/80 p-4 rounded-xl border border-blue-500/40 shadow-inner flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between text-xs font-bold text-blue-400 mb-2">
                            <span class="text-sm flex items-center gap-1.5">💵 Mini-Dólar (WDO) - Plano do Dia</span>
                            <span class="text-[10px] px-2 py-0.5 rounded border bg-blue-500/15 border-blue-500/40 uppercase font-black">{wdo['direction']}</span>
                        </div>
                        <p class="text-xs text-slate-200 leading-relaxed font-medium">{fp['wdo']}</p>
                    </div>
                    <div class="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                        <span>Preço de Referência: <strong class="text-blue-300 font-mono">{wdo.get('base_price', 'N/D')}</strong></span>
                        <span class="text-amber-400 font-mono font-semibold">{wdo.get('points_range', '')}</span>
                    </div>
                </div>

                <div class="bg-slate-950/80 p-4 rounded-xl border border-rose-500/30 shadow-inner flex flex-col justify-between">
                    <div>
                        <div class="flex items-center gap-1.5 text-xs font-bold text-rose-400 mb-2">
                            <span class="text-sm">⚠️ Zona de Perigo & Horários Críticos</span>
                        </div>
                        <p class="text-xs text-slate-300 leading-relaxed">{fp['danger']}</p>
                    </div>
                    <p class="text-[10px] text-slate-500 mt-2.5 pt-2 border-t border-slate-800/80">Regra de ouro: nunca abra ordens a mercado durante a formação de leilão.</p>
                </div>
            </div>

            <details class="mt-2.5 text-xs text-slate-500">
                <summary class="cursor-pointer text-slate-500 hover:text-slate-400 py-1 transition flex items-center gap-1.5 select-none">
                    <span>📊</span> <span>Leitura de Fundo do Mini-Índice (WIN) mantida em segundo plano (Oculto - Clique para expandir)</span>
                </summary>
                <div class="mt-1.5 p-3 bg-slate-950/70 rounded-xl border border-slate-800/70 text-slate-400 space-y-1">
                    <p><strong class="text-slate-300">Viés do WIN:</strong> <span class="text-emerald-400 font-bold">{win['direction']}</span> ({win['expected_range']})</p>
                    <p><strong class="text-slate-300">Resumo:</strong> {fp['win']}</p>
                </div>
            </details>

            <!-- Termômetro Visual de Estresse do Mercado (Barra 1 a 10) -->
            <div class="mt-3.5 pt-3 border-t border-slate-800/80">
                <div class="flex items-center justify-between text-xs mb-1.5">
                    <span class="text-slate-400 font-medium">Termômetro de Estresse / Ruído do Mercado:</span>
                    <span class="font-mono font-bold text-slate-200"><span class="text-amber-400">{risk_score}/10</span> — {risk_label}</span>
                </div>
                <div class="flex gap-1.5">
                    {risk_bars_html}
                </div>
            </div>
        </section>

        <!-- 1.5. MONITORAMENTO EM TEMPO REAL (PRÉ-MERCADO vs COTAÇÃO ATUAL) -->
        <section class="bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 border border-emerald-500/40 rounded-2xl p-4 sm:p-5 shadow-xl relative overflow-hidden">
            <div class="flex flex-wrap items-center justify-between gap-3 mb-3.5 pb-2.5 border-b border-slate-800">
                <div class="flex items-center gap-2">
                    <span class="relative flex h-3 w-3">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                    </span>
                    <h2 class="text-xs font-black uppercase tracking-wider text-emerald-400">
                        Painel Dinâmico: Pré-Mercado vs Tempo Real ao Vivo
                    </h2>
                </div>
                <div class="flex items-center gap-3">
                    <span id="liveStatusText" class="text-[11px] font-mono text-slate-300 flex items-center gap-1.5">
                        <span class="text-emerald-400 font-bold">● FEED CONECTADO</span>
                    </span>
                    <button onclick="refreshLiveMarket()" class="px-3 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-bold transition flex items-center gap-1 shadow-sm active:scale-95">
                        🔄 Atualizar Agora
                    </button>
                </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                <!-- Bitcoin Live -->
                <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between text-slate-400 mb-1">
                            <span class="font-bold text-slate-200">₿ Bitcoin (BTC/USD)</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold">Crypto 24h</span>
                        </div>
                        <div class="flex items-baseline justify-between mt-2">
                            <div>
                                <p class="text-[10px] text-slate-500">No Pré-Mkt: <span class="font-mono text-slate-300 font-semibold">{btc_asset_price}</span></p>
                                <p class="text-base font-black text-white font-mono mt-0.5" id="liveBtcPrice">Carregando...</p>
                            </div>
                            <span class="text-xs font-bold font-mono px-2 py-0.5 rounded" id="liveBtcChange">...</span>
                        </div>
                    </div>
                    <p class="text-[10px] text-slate-400 mt-2 border-t border-slate-800/80 pt-1.5" id="liveBtcSignal">Aguardando feed institucional...</p>
                </div>

                <!-- Dólar Comercial Live -->
                <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between text-slate-400 mb-1">
                            <span class="font-bold text-slate-200">💵 Dólar Comercial (USD/BRL)</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">Forex Live</span>
                        </div>
                        <div class="flex items-baseline justify-between mt-2">
                            <div>
                                <p class="text-[10px] text-slate-500">No Pré-Mkt: <span class="font-mono text-slate-300 font-semibold">R$ {usd_price}</span></p>
                                <p class="text-base font-black text-white font-mono mt-0.5" id="liveUsdPrice">Carregando...</p>
                            </div>
                            <span class="text-xs font-bold font-mono px-2 py-0.5 rounded" id="liveUsdChange">...</span>
                        </div>
                    </div>
                    <p class="text-[10px] text-slate-400 mt-2 border-t border-slate-800/80 pt-1.5" id="liveUsdSignal">Aguardando feed cambial...</p>
                </div>

                <!-- Euro / Dólar Live -->
                <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between text-slate-400 mb-1">
                            <span class="font-bold text-slate-200">🇪🇺 Euro / Dólar (EUR/USD)</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-bold">DXY Driver</span>
                        </div>
                        <div class="flex items-baseline justify-between mt-2">
                            <div>
                                <p class="text-[10px] text-slate-500">No Pré-Mkt: <span class="font-mono text-slate-300 font-semibold">{eur_price}</span></p>
                                <p class="text-base font-black text-white font-mono mt-0.5" id="liveEurPrice">Carregando...</p>
                            </div>
                            <span class="text-xs font-bold font-mono px-2 py-0.5 rounded" id="liveEurChange">...</span>
                        </div>
                    </div>
                    <p class="text-[10px] text-slate-400 mt-2 border-t border-slate-800/80 pt-1.5" id="liveEurSignal">Balizador do Dólar Global</p>
                </div>

                <!-- Relógio Oficial do Pregão e Status de Sessão -->
                <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between text-slate-400 mb-1">
                            <span class="font-bold text-slate-200">⏰ Sessão B3 & Wall Street</span>
                            <span class="text-xs font-mono font-bold text-amber-400" id="liveClock">--:--:-- BRT</span>
                        </div>
                        <div class="space-y-1.5 mt-2 text-[11px]" id="marketStatusPills">
                            <div class="flex items-center justify-between bg-slate-900 px-2 py-1 rounded border border-slate-800">
                                <span>Futuros B3 (WIN/WDO)</span>
                                <span class="font-bold font-mono" id="statusFuturos">Verificando...</span>
                            </div>
                            <div class="flex items-center justify-between bg-slate-900 px-2 py-1 rounded border border-slate-800">
                                <span>Mercado à Vista (Ações)</span>
                                <span class="font-bold font-mono" id="statusAVista">Verificando...</span>
                            </div>
                        </div>
                    </div>
                    <p class="text-[10px] text-slate-500 mt-2 border-t border-slate-800/80 pt-1">Horário Oficial de Brasília (GMT-3)</p>
                </div>
            </div>
        </section>

        <!-- 2. PLACAR DE ASSERTIVIDADE AUDITADA (ÚLTIMOS 60 PREGÕES) -->
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5 shadow-lg">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3.5 pb-2.5 border-b border-slate-800">
                <div class="flex items-center gap-2">
                    <span class="text-base">🎯</span>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300">
                        Índice de Assertividade Auditada (Mini-Dólar WDO)
                    </h2>
                    <span class="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40 font-bold">
                        Amostra oficial de {accuracy_metrics['total_days']} pregões
                    </span>
                </div>
                <span class="text-[11px] text-slate-400">Auditoria individualizada por alvo de trade e canal de variação</span>
            </div>

            <!-- Grid de 3 Cards de Assertividade -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3.5 mb-4">
                <!-- 1. Alvo 1 (Take 1 / Parcial) -->
                <div class="bg-slate-950/80 border border-emerald-500/30 rounded-xl p-4 flex flex-col justify-between shadow-inner">
                    <div>
                        <div class="flex items-center justify-between mb-1.5">
                            <span class="text-xs font-bold text-emerald-400 uppercase tracking-wider">🎯 Alvo 1 (Take 1 ~15 pts)</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 font-bold border border-emerald-500/30">1ª Parcial</span>
                        </div>
                        <p class="text-3xl font-black text-white font-mono mt-1">{accuracy_metrics['wdo_t1_accuracy']}%</p>
                        <p class="text-xs text-slate-400 mt-1">
                            <span class="text-emerald-400 font-bold">{accuracy_metrics['wdo_t1_hits']} acertos</span> em {accuracy_metrics['total_days']} pregões
                        </p>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-2.5 pt-2 border-t border-slate-800/80 leading-relaxed">
                        Taxa de dias em que o preço buscou a primeira parcial de 15 pontos do WDO antes da trava de stop.
                    </p>
                </div>

                <!-- 2. Alvo 2 (Expansão / Tendência) -->
                <div class="bg-slate-950/80 border border-blue-500/30 rounded-xl p-4 flex flex-col justify-between shadow-inner">
                    <div>
                        <div class="flex items-center justify-between mb-1.5">
                            <span class="text-xs font-bold text-blue-400 uppercase tracking-wider">🚀 Alvo 2 (Expansão ~35-40 pts)</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/15 text-blue-300 font-bold border border-blue-500/30">Tendência</span>
                        </div>
                        <p class="text-3xl font-black text-white font-mono mt-1">{accuracy_metrics['wdo_t2_accuracy']}%</p>
                        <p class="text-xs text-slate-400 mt-1">
                            <span class="text-blue-400 font-bold">{accuracy_metrics['wdo_t2_hits']} acertos</span> em {accuracy_metrics['total_days']} pregões
                        </p>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-2.5 pt-2 border-t border-slate-800/80 leading-relaxed">
                        Taxa de dias em que o fluxo institucional estendeu o movimento até o 2º alvo (~35 a 42 pts) na amplitude do pregão.
                    </p>
                </div>

                <!-- 3. Variação Projetada (Canal de Fechamento) -->
                <div class="bg-slate-950/80 border border-amber-500/30 rounded-xl p-4 flex flex-col justify-between shadow-inner">
                    <div>
                        <div class="flex items-center justify-between mb-1.5">
                            <span class="text-xs font-bold text-amber-400 uppercase tracking-wider">📊 Variação Projetada (Faixa)</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 font-bold border border-amber-500/30">Fechamento</span>
                        </div>
                        <p class="text-3xl font-black text-white font-mono mt-1">{accuracy_metrics['wdo_range_accuracy']}%</p>
                        <p class="text-xs text-slate-400 mt-1">
                            <span class="text-amber-400 font-bold">{accuracy_metrics['wdo_range_hits']} acertos</span> em {accuracy_metrics['total_days']} pregões
                        </p>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-2.5 pt-2 border-t border-slate-800/80 leading-relaxed">
                        Taxa de pregões em que o fechamento oficial B3 encerrou dentro da faixa de variação estimada.
                    </p>
                </div>
            </div>

            <!-- Metodologia e Fórmulas de Auditoria Matemática -->
            <div class="bg-slate-950/90 border border-slate-800 rounded-xl p-4 text-xs">
                <div class="flex items-center justify-between mb-2">
                    <span class="font-bold text-amber-400 flex items-center gap-1.5">
                        <span>📐</span> Base de Cálculo e Fórmulas Matemáticas da Auditoria:
                    </span>
                    <span class="text-[10px] text-slate-500 font-mono">Registro pré-leilão: 08:20 BRT</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-[11px] text-slate-300 pt-1">
                    <div class="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                        <strong class="text-emerald-400 block mb-1">1. Fórmula do Alvo 1:</strong>
                        <p class="text-slate-400 font-mono mb-1">Taxa = ({accuracy_metrics['wdo_t1_hits']} ÷ {accuracy_metrics['total_days']}) × 100 = <strong class="text-white">{accuracy_metrics['wdo_t1_accuracy']}%</strong></p>
                        <p class="text-slate-400 leading-tight">Mede a probabilidade de o trade atingir a 1ª parcial de 15 pontos a favor do viés antes de retornar na trava de stop.</p>
                    </div>
                    <div class="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                        <strong class="text-blue-400 block mb-1">2. Fórmula do Alvo 2:</strong>
                        <p class="text-slate-400 font-mono mb-1">Taxa = ({accuracy_metrics['wdo_t2_hits']} ÷ {accuracy_metrics['total_days']}) × 100 = <strong class="text-white">{accuracy_metrics['wdo_t2_accuracy']}%</strong></p>
                        <p class="text-slate-400 leading-tight">Mede a probabilidade de expansão da tendência em dias de forte fluxo institucional direcional (alvo longo).</p>
                    </div>
                    <div class="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
                        <strong class="text-amber-400 block mb-1">3. Fórmula da Faixa:</strong>
                        <p class="text-slate-400 font-mono mb-1">Taxa = ({accuracy_metrics['wdo_range_hits']} ÷ {accuracy_metrics['total_days']}) × 100 = <strong class="text-white">{accuracy_metrics['wdo_range_accuracy']}%</strong></p>
                        <p class="text-slate-400 leading-tight">Mede o enquadramento estatístico do fechamento oficial da B3 dentro da faixa percentual projetada de manhã.</p>
                    </div>
                </div>
                <p class="text-[10px] text-slate-500 mt-2.5 pt-2 border-t border-slate-800/80">
                    * Metodologia anti-viés: Todos os cenários e alvos são congelados no GitHub antes da abertura da B3 e auditados automaticamente com os dados oficiais de fechamento às 18:15 BRT.
                </p>
            </div>
        </section>

        <!-- 2.5. AUDITORIA VISUAL: GRÁFICO FIEL & CONFERÊNCIA DIÁRIA (PROJETADO vs PROFIT) -->
        <section class="bg-gradient-to-b from-slate-900/90 via-slate-900 to-slate-950 border-2 border-amber-500/30 rounded-2xl p-4 sm:p-5 shadow-2xl space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-xl shadow-inner">
                        📈
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h2 class="text-sm font-extrabold text-white tracking-tight">AUDITORIA VISUAL: GRÁFICO FIEL & CONFERÊNCIA DIÁRIA</h2>
                            <span class="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-bold border border-amber-500/40">PROJETADO vs PROFIT</span>
                        </div>
                        <p class="text-xs text-slate-400">Veja se os candles tocaram nos alvos projetados e ajuste os dados reais do seu pregão para calibrar o modelo</p>
                    </div>
                </div>

                <!-- Seletor de Pregão -->
                <div class="flex items-center gap-2 bg-slate-950/80 px-3 py-1.5 rounded-xl border border-slate-800 shadow-inner">
                    <span class="text-xs text-slate-400 font-medium">Pregão em Análise:</span>
                    <select id="auditDateSelect" onchange="onAuditDateSelected(this.value)" class="bg-slate-900 border border-slate-700 text-amber-400 text-xs font-mono font-bold rounded-lg px-2.5 py-1 focus:outline-none focus:border-amber-400 cursor-pointer">
                        <!-- Preenchido via JavaScript -->
                    </select>
                </div>
            </div>

            <!-- Importador Fiel Direto do ProfitChart (Arraste ou Selecione) -->
            <div id="profitDropZone" ondragover="handleProfitDragOver(event)" ondragleave="handleProfitDragLeave(event)" ondrop="handleProfitFileDrop(event)" class="bg-slate-950/80 border-2 border-dashed border-slate-700/80 hover:border-amber-400 rounded-xl p-3 transition flex flex-wrap items-center justify-between gap-3 shadow-inner">
                <div class="flex items-center gap-2.5 text-left">
                    <div class="w-9 h-9 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-lg shadow-sm">
                        ⚡
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="text-xs font-bold text-white">Importar Gráfico Oficial do ProfitChart (1 Minuto)</span>
                            <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 font-bold border border-emerald-500/30">Opção 1 Ativa</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Arraste aqui o arquivo exportado do seu Profit (.csv ou .txt) ou clique no botão ao lado para carregar</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <input type="file" id="profitFileInput" accept=".csv,.txt,.prt" onchange="handleProfitFileSelect(event)" class="hidden">
                    <button onclick="document.getElementById('profitFileInput').click()" class="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-yellow-300 text-slate-950 font-black text-xs transition shadow-md shadow-amber-500/20 active:scale-95 flex items-center gap-1.5 cursor-pointer">
                        <span>📂 Carregar CSV/TXT do Profit</span>
                    </button>
                    <span id="profitLoadedStatus" class="hidden text-[10px] font-bold text-emerald-400 bg-emerald-500/15 border border-emerald-500/30 px-2.5 py-1 rounded-lg"></span>
                </div>
            </div>

            <!-- Gráfico Interativo com Linhas Projetadas -->
            <div>
                <div class="flex flex-wrap items-center justify-between gap-3 mb-2.5">
                    <!-- Retângulo Azul: Seleção de Linhas com Cores Distintas (Sem Trava Stop) -->
                    <div class="flex flex-wrap items-center gap-2 text-xs font-mono">
                        <span class="text-slate-400 font-sans font-medium text-[11px] mr-0.5">Exibir Linhas:</span>
                        
                        <!-- Ponto Zero (Branco / Neutro) -->
                        <button onclick="toggleChartLine('base')" id="btnToggleBase" class="px-2.5 py-1 rounded-lg bg-slate-800 text-white border-2 border-slate-300 shadow-sm transition active:scale-95 flex items-center gap-1.5 cursor-pointer">
                            <span class="w-2 h-2 rounded-full bg-white inline-block shadow"></span>
                            <span>Ponto Zero: <strong id="lblChartBase">5.080,5</strong></span>
                        </button>

                        <!-- Alvo 1 (Azul Ciano) -->
                        <button onclick="toggleChartLine('t1')" id="btnToggleT1" class="px-2.5 py-1 rounded-lg bg-sky-500/20 text-sky-300 border-2 border-sky-400 shadow-sm shadow-sky-500/20 transition active:scale-95 flex items-center gap-1.5 cursor-pointer">
                            <span class="w-2 h-2 rounded-full bg-sky-400 inline-block shadow"></span>
                            <span>🎯 Alvo 1: <strong id="lblChartT1">5.065,5</strong></span>
                        </button>

                        <!-- Alvo 2 (Roxo / Púrpura) -->
                        <button onclick="toggleChartLine('t2')" id="btnToggleT2" class="px-2.5 py-1 rounded-lg bg-purple-500/20 text-purple-300 border-2 border-purple-400 shadow-sm shadow-purple-500/20 transition active:scale-95 flex items-center gap-1.5 cursor-pointer">
                            <span class="w-2 h-2 rounded-full bg-purple-400 inline-block shadow"></span>
                            <span>🚀 Alvo 2: <strong id="lblChartT2">5.040,0</strong></span>
                        </button>
                    </div>

                    <!-- Retângulo Laranja: Seleção de Tempos Gráficos (1m, 5m, 15m, 1h, Diário) -->
                    <div class="flex items-center gap-1 bg-slate-950/90 p-1 rounded-xl border-2 border-amber-500/60 shadow-lg shadow-amber-500/10">
                        <span class="text-[10px] text-amber-400 font-sans px-1.5 font-bold hidden sm:inline">Tempo:</span>
                        <button onclick="switchChartTimeframe('1m')" id="tfBtn_1m" class="px-2.5 py-1 text-xs rounded-lg font-bold font-mono transition bg-amber-500 text-slate-950 font-black shadow-md cursor-pointer">1m</button>
                        <button onclick="switchChartTimeframe('5m')" id="tfBtn_5m" class="px-2.5 py-1 text-xs rounded-lg font-bold font-mono transition bg-slate-900 text-slate-400 hover:text-white border border-slate-800 cursor-pointer">5m</button>
                        <button onclick="switchChartTimeframe('15m')" id="tfBtn_15m" class="px-2.5 py-1 text-xs rounded-lg font-bold font-mono transition bg-slate-900 text-slate-400 hover:text-white border border-slate-800 cursor-pointer">15m</button>
                        <button onclick="switchChartTimeframe('1h')" id="tfBtn_1h" class="px-2.5 py-1 text-xs rounded-lg font-bold font-mono transition bg-slate-900 text-slate-400 hover:text-white border border-slate-800 cursor-pointer">1h</button>
                        <button onclick="switchChartTimeframe('D')" id="tfBtn_D" class="px-2.5 py-1 text-xs rounded-lg font-bold font-mono transition bg-slate-900 text-slate-400 hover:text-white border border-slate-800 cursor-pointer">Diário</button>
                    </div>
                </div>

                <!-- Container do Gráfico TradingView Lightweight Charts -->
                <div id="wdoChartContainer" class="w-full h-[380px] rounded-xl overflow-hidden bg-slate-950 border border-slate-800 shadow-inner relative">
                    <div id="chartFallback" class="hidden absolute inset-0 flex items-center justify-center text-xs text-slate-500">
                        Carregando visualizador gráfico...
                    </div>
                </div>
            </div>

            <!-- Painel Comparativo Lado a Lado: Projetado vs O Que Aconteceu no Profit -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-1">
                
                <!-- Coluna 1: O Que o Radar Projetou -->
                <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-inner">
                    <div>
                        <div class="flex items-center justify-between pb-2 mb-2.5 border-b border-slate-800/80">
                            <span class="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                                <span>🔮</span> O Que o Sistema Projetou às 08:20 BRT:
                            </span>
                            <span id="projDateBadge" class="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">--</span>
                        </div>
                        <div class="space-y-2 text-xs font-mono">
                            <div class="flex items-center justify-between py-1 border-b border-slate-900">
                                <span class="font-sans text-slate-400">Viés Indicado:</span>
                                <span id="projBiasText" class="font-bold text-sm text-rose-400">--</span>
                            </div>
                            <div class="flex items-center justify-between py-1 border-b border-slate-900">
                                <span class="font-sans text-slate-400">Faixa de Variação (%):</span>
                                <span id="projRangeText" class="font-bold text-slate-200">--</span>
                            </div>
                            <div class="flex items-center justify-between py-1 border-b border-slate-900">
                                <span class="font-sans text-slate-400">Ponto Zero (Fech. Anterior):</span>
                                <span id="projBaseText" class="font-bold text-slate-200">--</span>
                            </div>
                            <div class="flex items-center justify-between py-1 border-b border-slate-900">
                                <span class="font-sans text-slate-400">🎯 Linha Alvo 1 (Take 1):</span>
                                <span id="projT1Text" class="font-bold text-sky-400">--</span>
                            </div>
                            <div class="flex items-center justify-between py-1">
                                <span class="font-sans text-slate-400">🚀 Linha Alvo 2 (Expansão):</span>
                                <span id="projT2Text" class="font-bold text-purple-400">--</span>
                            </div>
                        </div>
                    </div>
                    <p class="text-[10px] text-slate-500 mt-2.5 pt-2 border-t border-slate-900">Estes dados foram congelados antes da abertura e servem de régua para a auditoria.</p>
                </div>

                <!-- Coluna 2: O Que de Fato Aconteceu no seu ProfitChart -->
                <div class="bg-slate-950/80 border border-blue-500/30 rounded-xl p-4 flex flex-col justify-between shadow-inner">
                    <div>
                        <div class="flex items-center justify-between pb-2 mb-2.5 border-b border-slate-800/80">
                            <span class="text-xs font-bold text-blue-400 flex items-center gap-1.5">
                                <span>🎯</span> O Que De Fato Aconteceu no seu ProfitChart:
                            </span>
                            <span class="text-[10px] text-slate-500 font-sans">Editável para calibração</span>
                        </div>

                        <!-- 3 Inputs Editáveis -->
                        <div class="grid grid-cols-3 gap-2.5 mb-3">
                            <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                                <label class="text-[10px] text-slate-400 block font-medium mb-1 font-sans">Máxima Real:</label>
                                <input type="number" step="0.5" id="inpAuditHigh" oninput="onAuditValuesChanged()" class="w-full bg-slate-950 border border-slate-700 text-white font-mono font-bold text-xs rounded px-2 py-1 focus:outline-none focus:border-blue-400 text-center">
                            </div>
                            <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                                <label class="text-[10px] text-slate-400 block font-medium mb-1 font-sans">Mínima Real:</label>
                                <input type="number" step="0.5" id="inpAuditLow" oninput="onAuditValuesChanged()" class="w-full bg-slate-950 border border-slate-700 text-white font-mono font-bold text-xs rounded px-2 py-1 focus:outline-none focus:border-blue-400 text-center">
                            </div>
                            <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                                <label class="text-[10px] text-slate-400 block font-medium mb-1 font-sans">Fechamento Real:</label>
                                <input type="number" step="0.5" id="inpAuditClose" oninput="onAuditValuesChanged()" class="w-full bg-slate-950 border border-slate-700 text-white font-mono font-bold text-xs rounded px-2 py-1 focus:outline-none focus:border-blue-400 text-center">
                            </div>
                        </div>

                        <!-- Checklist Automático de Auditoria -->
                        <div class="space-y-1.5 text-xs">
                            <div class="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                                <span class="font-sans text-slate-300">🎯 Bateu Alvo 1 (~15 pts)?</span>
                                <span id="auditChkTarget1" class="font-bold text-xs">--</span>
                            </div>
                            <div class="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                                <span class="font-sans text-slate-300">🚀 Bateu Alvo 2 (~35-40 pts)?</span>
                                <span id="auditChkTarget2" class="font-bold text-xs">--</span>
                            </div>
                            <div class="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                                <span class="font-sans text-slate-300">📊 Fechamento dentro da Faixa?</span>
                                <span id="auditChkRange" class="font-bold text-xs">--</span>
                            </div>
                            <div class="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                                <span class="font-sans text-slate-300">✔ Validação do Trader:</span>
                                <button onclick="toggleDayAuditedStatus()" id="btnMarkAudited" class="px-2.5 py-0.5 rounded-lg text-[11px] font-bold border transition cursor-pointer">
                                    <span id="lblMarkAudited">Conferir</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Botões de Ação -->
                    <div class="mt-3.5 pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2">
                        <button onclick="saveCurrentAuditDay()" id="btnSaveAudit" class="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white font-bold text-xs flex items-center gap-1.5 transition shadow-lg">
                            <span>💾</span> <span>Salvar Auditoria do Pregão</span>
                        </button>
                        <div class="flex items-center gap-2">
                            <button onclick="copyAuditDaySummary()" class="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-700 transition flex items-center gap-1">
                                <span>📋</span> <span>Copiar Resumo</span>
                            </button>
                            <button onclick="exportAuditDatasetJson()" class="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-700 transition flex items-center gap-1">
                                <span>📥</span> <span>Baixar JSON</span>
                            </button>
                        </div>
                    </div>
                </div>

            </div>
            
            <div id="auditToastMsg" class="hidden p-3 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-bold flex items-center justify-between">
                <span id="auditToastText">✔ Auditoria salva com sucesso!</span>
                <button onclick="document.getElementById('auditToastMsg').classList.add('hidden')" class="text-emerald-400 hover:text-white">✕</button>
            </div>
        </section>

        <!-- 3. O CORAÇÃO DO TRADE: MINI-DÓLAR (WDO) EM DESTAQUE -->
        <section class="space-y-4">
            
            <!-- CARD PRINCIPAL: MINI-DÓLAR (WDO) -->
            <div class="bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 border-2 border-blue-500/50 hover:border-blue-400/80 transition rounded-2xl p-5 sm:p-6 shadow-2xl relative overflow-hidden">
                <div class="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
                
                <div class="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-2xl shadow-inner">
                            💵
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <h2 class="text-base font-extrabold text-white tracking-tight">MINI-DÓLAR FUTURO (WDO)</h2>
                                <span class="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-bold border border-blue-500/40">ATIVO EM OPERAÇÃO</span>
                            </div>
                            <p class="text-xs text-slate-400">Abertura: 09:00 BRT | Leilão: 08:50 BRT | Variação mínima: 0.5 pt (R$ 5,00/contrato)</p>
                        </div>
                    </div>
                    <span class="px-4 py-1.5 text-xs font-black rounded-xl border {wdo_badge_class} flex items-center gap-1.5 shadow-lg">
                        <span>{wdo.get('trend_badge', wdo_dir)}</span>
                    </span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Bloco Vertical de Níveis e Projeções -->
                    <div class="bg-slate-950/90 border border-slate-800 rounded-xl p-4 font-mono text-xs space-y-2.5 shadow-inner">
                        <div class="flex items-center justify-between border-b border-slate-800/80 pb-2 font-sans">
                            <span class="text-slate-400 font-medium">Projeção Estimada (%):</span>
                            <span class="font-black {wdo_text_color} font-mono text-sm">{wdo['expected_range']}</span>
                        </div>
                        <div class="flex items-center justify-between border-b border-slate-800/80 pb-2 font-sans">
                            <span class="text-slate-400 font-medium">Amplitude Projetada (Pts):</span>
                            <span class="font-bold text-amber-400 font-mono">{wdo.get('points_range', 'N/D')}</span>
                        </div>
                        <div class="flex items-center justify-between border-b border-slate-800/80 pb-2 font-sans">
                            <span class="text-slate-400 font-medium">Faixa das Linhas:</span>
                            <span class="font-bold text-blue-300 font-mono text-[11px]">{wdo.get('range_prices_str', '')}</span>
                        </div>
                        <div class="flex items-center justify-between py-0.5">
                            {wdo_t1_html}
                        </div>
                        <div class="flex items-center justify-between py-0.5">
                            {wdo_t2_html}
                        </div>
                        <div class="flex items-center justify-between border-t border-slate-800/80 pt-2">
                            {wdo_trava_html}
                        </div>
                    </div>

                    <!-- Catalisador e Contexto Macroeconômico -->
                    <div class="flex flex-col justify-between space-y-3">
                        <div class="bg-slate-950/60 border border-slate-800 rounded-xl p-4 flex-1">
                            <span class="text-amber-400 font-bold flex items-center gap-1.5 text-xs mb-2">
                                <span>⚡</span> Catalisador Principal do Câmbio:
                            </span>
                            <p class="text-xs text-slate-200 leading-relaxed">{wdo['catalyst']}</p>
                        </div>
                        
                        <div class="bg-blue-950/20 border border-blue-500/20 rounded-xl p-3 flex items-center justify-between text-xs">
                            <span class="text-slate-400">Preço de Fechamento Base (Fch):</span>
                            <span class="font-mono font-bold text-blue-300">{wdo.get('base_price', '5.080,5 pts')}</span>
                        </div>
                    </div>
                </div>

                <!-- TABELA DIRETA: ONDE PLOTAR CADA LINHA NO PROFITCHART -->
                <div class="mt-4 pt-3.5 border-t border-slate-800/80">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                            <span>📐</span> Coordenadas Prontas para Digitar no seu ProfitChart (WDOX26):
                        </span>
                        <span class="text-[10px] text-slate-500 font-mono">Tick B3: 0.5 pt</span>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs font-mono">
                        <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                            <span class="text-[10px] text-slate-400 block font-sans mb-0.5">Ponto Zero (Fechamento):</span>
                            <span class="text-white font-extrabold text-sm">{wdo.get('base_price', '5.080.5 pts')}</span>
                            <span class="text-[10px] text-slate-500 block mt-0.5">Referência de Sexta</span>
                        </div>
                        <div class="bg-slate-950/80 p-3 rounded-xl border border-rose-500/30">
                            <span class="text-[10px] text-rose-400/90 block font-sans mb-0.5">Linha Alvo 1 ({wdo.get('pts_t1', '')}):</span>
                            <span class="text-rose-400 font-extrabold text-sm">{wdo.get('line_t1', '')}</span>
                            <span class="text-[10px] text-slate-400 block mt-0.5">Take 1 (Sua linha 5.054)</span>
                        </div>
                        <div class="bg-slate-950/80 p-3 rounded-xl border border-rose-500/30">
                            <span class="text-[10px] text-rose-400/90 block font-sans mb-0.5">Linha Alvo 2 ({wdo.get('pts_t2', '')}):</span>
                            <span class="text-rose-400 font-extrabold text-sm">{wdo.get('line_t2', '')}</span>
                            <span class="text-[10px] text-slate-400 block mt-0.5">Take 2 (Sua linha 5.045)</span>
                        </div>
                        <div class="bg-slate-950/80 p-3 rounded-xl border border-amber-500/30">
                            <span class="text-[10px] text-amber-400/90 block font-sans mb-0.5">Trava de Stop ({wdo.get('pts_stop', '')}):</span>
                            <span class="text-amber-400 font-extrabold text-sm">{wdo.get('line_stop', '')}</span>
                            <span class="text-[10px] text-slate-400 block mt-0.5">Stop Loss / Invalidação</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Mini-Índice (WIN) Oculto / Segundo Plano -->
            <details class="text-xs text-slate-500">
                <summary class="cursor-pointer text-slate-500 hover:text-slate-400 py-1 transition flex items-center gap-1.5 font-medium select-none">
                    <span>📊</span> <span>Mini-Índice (WIN) mantido em segundo plano (Oculto - Clique para exibir se necessário)</span>
                </summary>
                <div class="mt-2 p-4 bg-slate-950/70 border border-slate-800/80 rounded-xl space-y-2 text-slate-300">
                    <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                        <span class="font-bold text-white flex items-center gap-2">📊 MINI-ÍNDICE (WIN)</span>
                        <span class="px-2.5 py-0.5 rounded text-[11px] font-bold border {win_badge_class}">{win.get('trend_badge', win_dir)}</span>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono pt-1">
                        <div><span class="text-slate-500 block text-[10px] font-sans">Projeção:</span>{win['expected_range']}</div>
                        <div><span class="text-slate-500 block text-[10px] font-sans">Alvo 1:</span>{win.get('target_1_val', win.get('target_1'))}</div>
                        <div><span class="text-slate-500 block text-[10px] font-sans">Alvo 2:</span>{win.get('target_2_val', win.get('target_2'))}</div>
                        <div><span class="text-slate-500 block text-[10px] font-sans">Stop Trava:</span>{win.get('trava_val', win.get('trava_risco'))}</div>
                    </div>
                    <p class="text-[11px] text-slate-400 pt-1.5 border-t border-slate-800/80"><strong class="text-amber-400/90 font-medium">Catalisador WIN:</strong> {win['catalyst']}</p>
                </div>
            </details>
        </section>

        <!-- 4. PRÉ-MERCADO DE NOVA YORK (ADRs BRASIL) & CÂMBIO -->
        <section class="bg-gradient-to-r from-slate-900 to-slate-950 border border-amber-500/30 rounded-2xl p-4 sm:p-5 shadow-lg">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                        <span>🔥</span> Pré-Mercado de Nova York (ADRs Brasil em Wall Street)
                    </h2>
                    <p class="text-[11px] text-slate-400">Negociações a partir das 05h BRT em NY: antecipam a abertura de Petrobras, Vale, Itaú e Ibovespa</p>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold uppercase">Alta Relevância</span>
            </div>

            <!-- Destaque do Dólar no Pré-Mercado -->
            <div class="mb-3.5 p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-wrap items-center justify-between gap-2">
                <div class="flex items-center gap-2.5">
                    <span class="text-lg">💵</span>
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="text-xs font-bold text-white">DÓLAR NO PRÉ-MERCADO INTERNACIONAL (FOREX)</span>
                            <span class="px-2 py-0.5 rounded text-[10px] font-black border uppercase {dollar_premarket_style}">{dollar_premarket_badge}</span>
                        </div>
                        <p class="text-[11px] text-slate-400 mt-0.5">{dollar_premarket_desc}</p>
                    </div>
                </div>
                <span class="text-[10px] text-slate-500 font-mono">Forex 24h</span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {adrs_html}
            </div>
        </section>

        <!-- 5. COMMODITIES GLOBAIS (PETRÓLEO, GÁS, MINÉRIO, OURO) -->
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                        <span>⛏️</span> Commodities Globais (Minério, Petróleo, Gás & Ouro)
                    </h2>
                    <p class="text-[11px] text-slate-400">Termômetro industrial, energético e ativo de proteção global</p>
                </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {commodities_html}
            </div>
        </section>

        <!-- 6. WALL STREET, JUROS & MOEDAS GLOBAIS -->
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                        <span>🌐</span> Wall Street, Volatilidade (VIX), Câmbio & Ásia
                    </h2>
                    <p class="text-[11px] text-slate-400">Índices americanos, DXY, Treasury 10 Anos e bolsas asiáticas</p>
                </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {macro_html}
            </div>
        </section>

        <!-- 7. FOREX & CRYPTO: APETITE A RISCO & CESTA CAMBIAL -->
        <section class="bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 border border-blue-500/30 rounded-2xl p-4 sm:p-5 shadow-lg">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-2">
                        <span>⚡</span> Crypto & Forex (Apetite a Risco Global & Cesta Cambial)
                    </h2>
                    <p class="text-[11px] text-slate-400">Bitcoin baliza apetite a risco 24/7; USD/MXN (México) e EUR/USD balizam a força real do Dólar</p>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold uppercase">Liquidez 24h</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {forex_crypto_html}
            </div>
        </section>

        <!-- 8. MERCADO DE TRABALHO & CALENDÁRIO DE RISCO -->
        <section class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            
            <!-- Indicadores de Emprego -->
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5">
                <div class="flex items-center justify-between mb-3">
                    <h2 class="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-2">
                        <span>💼</span> Mercado de Trabalho & Emprego
                    </h2>
                    <span class="text-[10px] text-slate-500">EUA & Brasil</span>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {labor_html}
                </div>
            </div>

            <!-- Régua de Horários Críticos -->
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5">
                <div class="flex items-center justify-between mb-3">
                    <h2 class="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-2">
                        <span>⚠️</span> Régua de Horários Críticos do Pregão
                    </h2>
                    <span class="text-[10px] text-slate-500">Picos de Volatilidade</span>
                </div>
                <div class="space-y-2">
                    {calendar_html}
                </div>
            </div>

        </section>

        <!-- 8. NOTÍCIAS & CATALISADORES (RETRÁTIL / ACORDEÃO) -->
        <details open class="group bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5 transition">
            <summary class="flex items-center justify-between cursor-pointer list-none select-none">
                <div class="flex items-center gap-2">
                    <span>📰</span>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300">
                        Noticiário & Catalisadores das Últimas 4h e 24h
                    </h2>
                    <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">7 Categorias</span>
                </div>
                <span class="text-xs text-amber-400 font-bold group-open:rotate-180 transition-transform">▼</span>
            </summary>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 mt-4 pt-3 border-t border-slate-800">
                {news_sections}
            </div>
        </details>

        <!-- 9. HISTÓRICO DE AUDITORIA DE ASSERTIVIDADE (RETRÁTIL) -->
        <details class="group bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5 transition">
            <summary class="flex items-center justify-between cursor-pointer list-none select-none">
                <div class="flex items-center gap-2">
                    <span>📋</span>
                    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300">
                        Auditoria de Assertividade (Histórico dos Pregões Anteriores)
                    </h2>
                    <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">Conferência dos 60 Dias</span>
                </div>
                <span class="text-xs text-slate-400 font-bold group-open:rotate-180 transition-transform">▼</span>
            </summary>
            
            <div class="overflow-x-auto mt-4 pt-3 border-t border-slate-800">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-slate-800 text-[10px] uppercase tracking-wider text-slate-400 font-semibold bg-slate-950/40">
                            <th class="py-2.5 px-3">Data</th>
                            <th class="py-2.5 px-3">Viés WDO</th>
                            <th class="py-2.5 px-3">Alvo 1 (~15 pts)</th>
                            <th class="py-2.5 px-3">Alvo 2 (~35 pts)</th>
                            <th class="py-2.5 px-3">Faixa Estimada</th>
                            <th class="py-2.5 px-3">Fech. Real B3</th>
                            <th class="py-2.5 px-3">Status Faixa</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history_rows}
                    </tbody>
                </table>
            </div>
        </details>

    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800/80 mt-10 py-6 text-center text-xs text-slate-500">
        <p>Radar Day Trade B3 | Atualizado diariamente 20 min antes da abertura dos futuros | Foco em disciplina e travas operacionais.</p>
    </footer>

    <!-- Script de Cópia Rápida -->
    <script>
        function copyTradePlan() {{
            const text = `🎯 PLANO DE TRADE WDO - MINI-DÓLAR ({today_str})\\n\\n💵 VIÉS DO DÓLAR: {wdo['direction']}\\n• Ponto Zero (Fechamento Sexta): {wdo.get('base_price', '5.080,5 pts')} (Ajuste B3: 5.090,2 pts)\\n• Projeção Estimada: {wdo['expected_range']} ({wdo.get('points_range')})\\n\\n📐 COORDENADAS DAS LINHAS PARA O PROFITCHART (WDOX26):\\n• 🎯 Linha Alvo 1 ({wdo.get('pts_t1')}): {wdo.get('line_t1')} (Take 1 / Linha 5.054 do gráfico)\\n• 🎯 Linha Alvo 2 ({wdo.get('pts_t2')}): {wdo.get('line_t2')} (Take 2 / Linha 5.045 do gráfico)\\n• 🛡️ Linha Trava de Stop ({wdo.get('pts_stop')}): {wdo.get('line_stop')} (Proteção / Invalidação)\\n\\n⚡ Catalisador: {wdo['catalyst']}\\n⚠️ Zona de Perigo: {fp['danger']}`;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById('copyBtn');
                btn.innerText = '✔ Níveis do Dólar Copiados!';
                btn.classList.add('bg-blue-500', 'text-white');
                setTimeout(() => {{
                    btn.innerText = '📋 Copiar Níveis do Dólar (WDO)';
                    btn.classList.remove('bg-blue-500', 'text-white');
                }}, 2500);
            }});
        }}

        // --- Trava de Segurança por E-mail + Senha (Salvo no Dispositivo) ---
        const AUTH_CONFIG = {{
            allowedEmail: "adm.grupokauss@gmail.com",
            passHash: "beb6e93cddca4c4887f15b90078f73354cc2ebf3a4bb9ce105ae669b15e83e34",
            plainPass: "Eduardinho*102030"
        }};

        const AUTH_SESSION_KEY = 'kauss_auth_verified_v3';

        function isSessionVerified() {{
            try {{
                return localStorage.getItem(AUTH_SESSION_KEY) === 'VERIFIED_SESSION_2026' ||
                       sessionStorage.getItem(AUTH_SESSION_KEY) === 'VERIFIED_SESSION_2026';
            }} catch(e) {{
                return false;
            }}
        }}

        function setSessionVerified(remember) {{
            try {{
                if (remember) {{
                    localStorage.setItem(AUTH_SESSION_KEY, 'VERIFIED_SESSION_2026');
                    localStorage.setItem('kauss_radar_email', AUTH_CONFIG.allowedEmail);
                }} else {{
                    sessionStorage.setItem(AUTH_SESSION_KEY, 'VERIFIED_SESSION_2026');
                    sessionStorage.setItem('kauss_radar_email', AUTH_CONFIG.allowedEmail);
                }}
            }} catch(e) {{}}
        }}

        function clearSession() {{
            try {{
                localStorage.removeItem(AUTH_SESSION_KEY);
                localStorage.removeItem('kauss_radar_email');
                sessionStorage.removeItem(AUTH_SESSION_KEY);
                sessionStorage.removeItem('kauss_radar_email');
            }} catch(e) {{}}
        }}

        function updateUserDisplay(email) {{
            const badge = document.getElementById('userAuthBadge');
            const span = document.getElementById('userEmailSpan');
            if (badge && span && email) {{
                span.innerText = email;
                badge.classList.remove('hidden');
                badge.classList.add('flex');
            }}
        }}

        async function sha256Hex(str) {{
            try {{
                const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
                return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
            }} catch(e) {{
                return null;
            }}
        }}

        async function handleEmailLogin() {{
            const emailEl = document.getElementById('authEmailInput');
            const passEl = document.getElementById('authPasswordInput');
            const email = emailEl ? emailEl.value.trim().toLowerCase() : '';
            const password = passEl ? passEl.value.trim() : '';
            const rememberEl = document.getElementById('rememberEmail');
            const remember = rememberEl ? rememberEl.checked : true;
            const errorMsg = document.getElementById('authErrorMsg');
            const modal = document.getElementById('authLockModal');

            let isPassValid = false;
            if (password === AUTH_CONFIG.plainPass) {{
                isPassValid = true;
            }} else {{
                const hash = await sha256Hex(password);
                if (hash && hash === AUTH_CONFIG.passHash) {{
                    isPassValid = true;
                }}
            }}

            const isEmailValid = (email === AUTH_CONFIG.allowedEmail);

            if (isEmailValid && isPassValid) {{
                setSessionVerified(remember);
                if (modal) modal.classList.add('hidden');
                document.body.classList.remove('overflow-hidden');
                updateUserDisplay(email);
                if (errorMsg) errorMsg.classList.add('hidden');
            }} else {{
                if (errorMsg) {{
                    if (!isEmailValid) {{
                        errorMsg.innerText = 'E-mail não autorizado para este radar.';
                    }} else {{
                        errorMsg.innerText = 'Senha incorreta. Verifique e tente novamente.';
                    }}
                    errorMsg.classList.remove('hidden');
                }}
                if (!isEmailValid && emailEl) {{
                    emailEl.classList.add('border-rose-500');
                    emailEl.focus();
                }} else if (passEl) {{
                    passEl.classList.add('border-rose-500');
                    passEl.value = '';
                    passEl.focus();
                }}
            }}
        }}

        function logoutEmail() {{
            clearSession();
            location.reload();
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            const verified = isSessionVerified();
            const modal = document.getElementById('authLockModal');
            const emailInput = document.getElementById('authEmailInput');
            const passInput = document.getElementById('authPasswordInput');

            if (verified && modal) {{
                modal.classList.add('hidden');
                document.body.classList.remove('overflow-hidden');
                updateUserDisplay(AUTH_CONFIG.allowedEmail);
            }} else if (modal) {{
                document.body.classList.add('overflow-hidden');
                if (emailInput) {{
                    emailInput.value = AUTH_CONFIG.allowedEmail;
                }}
                if (passInput) {{
                    passInput.value = '';
                    setTimeout(() => passInput.focus(), 150);
                }}
            }}

            if (emailInput) {{
                emailInput.addEventListener('keyup', (e) => {{
                    if (e.key === 'Enter') {{
                        if (passInput && !passInput.value) passInput.focus();
                        else handleEmailLogin();
                    }}
                }});
            }}

            if (passInput) {{
                passInput.addEventListener('keyup', (e) => {{
                    if (e.key === 'Enter') handleEmailLogin();
                }});
            }}
        }});

        // --- Sincronizador de Mercado em Tempo Real ---
        async function fetchLiveBtc() {{
            try {{
                const res = await fetch('https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT');
                if (res.ok) {{
                    const d = await res.json();
                    const p = parseFloat(d.lastPrice);
                    const chg = parseFloat(d.priceChangePercent);
                    const elPrice = document.getElementById('liveBtcPrice');
                    const elChg = document.getElementById('liveBtcChange');
                    const elSig = document.getElementById('liveBtcSignal');
                    if (elPrice && !isNaN(p)) elPrice.innerText = '$ ' + p.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                    if (elChg && !isNaN(chg)) {{
                        elChg.innerText = (chg >= 0 ? '+' : '') + chg.toFixed(2) + '%';
                        elChg.className = 'text-xs font-bold font-mono px-2 py-0.5 rounded ' + (chg >= 0 ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20' : 'text-rose-400 bg-rose-500/10 border border-rose-500/20');
                    }}
                    if (elSig && !isNaN(chg)) {{
                        elSig.innerText = chg > 1.0 ? '🚀 Apetite a risco global firme (positivo para Bolsa)' : (chg < -1.0 ? '⚠️ Cautela com liquidez e aversão a risco' : 'Equilíbrio nas criptomoedas');
                    }}
                }}
            }} catch (e) {{ console.log('BTC live info:', e); }}
        }}

        async function fetchLiveForex() {{
            try {{
                const res = await fetch('https://economia.awesomeapi.com.br/last/USD-BRL,EUR-USD');
                if (res.ok) {{
                    const d = await res.json();
                    if (d.USDBRL) {{
                        const usdP = parseFloat(d.USDBRL.bid);
                        const usdChg = parseFloat(d.USDBRL.pctChange);
                        const elP = document.getElementById('liveUsdPrice');
                        const elC = document.getElementById('liveUsdChange');
                        const elS = document.getElementById('liveUsdSignal');
                        if (elP && !isNaN(usdP)) elP.innerText = 'R$ ' + usdP.toFixed(4);
                        if (elC && !isNaN(usdChg)) {{
                            elC.innerText = (usdChg >= 0 ? '+' : '') + usdChg.toFixed(2) + '%';
                            elC.className = 'text-xs font-bold font-mono px-2 py-0.5 rounded ' + (usdChg >= 0 ? 'text-rose-400 bg-rose-500/10 border border-rose-500/20' : 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20');
                        }}
                        if (elS && !isNaN(usdChg)) {{
                            elS.innerText = usdChg > 0.3 ? '▲ Pressão compradora no Dólar' : (usdChg < -0.3 ? '▼ Entrada de fluxo vendedor no Dólar' : 'Dólar estável no intradiário');
                        }}
                    }}
                    if (d.EURUSD) {{
                        const eurP = parseFloat(d.EURUSD.bid);
                        const eurChg = parseFloat(d.EURUSD.pctChange);
                        const elP = document.getElementById('liveEurPrice');
                        const elC = document.getElementById('liveEurChange');
                        if (elP && !isNaN(eurP)) elP.innerText = '$ ' + eurP.toFixed(4);
                        if (elC && !isNaN(eurChg)) {{
                            elC.innerText = (eurChg >= 0 ? '+' : '') + eurChg.toFixed(2) + '%';
                            elC.className = 'text-xs font-bold font-mono px-2 py-0.5 rounded ' + (eurChg >= 0 ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20' : 'text-rose-400 bg-rose-500/10 border border-rose-500/20');
                        }}
                    }}
                }}
            }} catch (e) {{ console.log('Forex live info:', e); }}
        }}

        function updateClockAndSessions() {{
            const now = new Date();
            const brtTime = new Intl.DateTimeFormat('pt-BR', {{
                timeZone: 'America/Sao_Paulo',
                hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
            }}).format(now);
            const elClock = document.getElementById('liveClock');
            if (elClock) elClock.innerText = brtTime + ' BRT';

            const parts = brtTime.split(':');
            const h = parseInt(parts[0], 10);
            const m = parseInt(parts[1], 10);
            const totalMin = h * 60 + m;

            const elFut = document.getElementById('statusFuturos');
            const elVista = document.getElementById('statusAVista');

            if (elFut) {{
                if (totalMin >= 540 && totalMin < 1080) {{
                    elFut.innerHTML = '<span class="text-emerald-400 font-bold">🟢 ABERTO</span>';
                }} else if (totalMin >= 530 && totalMin < 540) {{
                    elFut.innerHTML = '<span class="text-amber-400 font-bold">🟡 LEILÃO</span>';
                }} else {{
                    elFut.innerHTML = '<span class="text-slate-500 font-bold">🔴 FECHADO</span>';
                }}
            }}

            if (elVista) {{
                if (totalMin >= 600 && totalMin < 1020) {{
                    elVista.innerHTML = '<span class="text-emerald-400 font-bold">🟢 ABERTO</span>';
                }} else if (totalMin >= 585 && totalMin < 600) {{
                    elVista.innerHTML = '<span class="text-amber-400 font-bold">🟡 LEILÃO</span>';
                }} else {{
                    elVista.innerHTML = '<span class="text-slate-500 font-bold">🔴 FECHADO</span>';
                }}
            }}
        }}

        function refreshLiveMarket() {{
            fetchLiveBtc();
            fetchLiveForex();
            updateClockAndSessions();
            const el = document.getElementById('liveStatusText');
            if (el) {{
                el.innerHTML = '<span class="text-emerald-400 font-bold">✔ ATUALIZADO</span>';
                setTimeout(() => {{
                    el.innerHTML = '<span class="text-emerald-400 font-bold">● FEED CONECTADO</span>';
                }}, 2000);
            }}
        }}

        // ==========================================
        // AUDITORIA VISUAL DO WDO (CANDLES + LINHAS)
        // ==========================================
        const SERVER_AUDIT_RECORDS = {records_json};
        let AUDIT_RECORDS = [];
        let wdoChart = null;
        let candleSeries = null;
        let priceLines = [];
        let CURRENT_TIMEFRAME = '1m';
        let VISIBLE_LINES = {{
            base: true,
            t1: true,
            t2: true
        }};

        function loadStoredAuditData() {{
            try {{
                const stored = localStorage.getItem('RADAR_WDO_AUDIT_DATA');
                if (stored) {{
                    const parsed = JSON.parse(stored);
                    if (Array.isArray(parsed) && parsed.length > 0) {{
                        return parsed;
                    }}
                }}
            }} catch(e) {{}}
            return JSON.parse(JSON.stringify(SERVER_AUDIT_RECORDS));
        }}

        function saveStoredAuditData(data) {{
            try {{
                localStorage.setItem('RADAR_WDO_AUDIT_DATA', JSON.stringify(data));
            }} catch(e) {{}}
        }}

        function initAuditChart() {{
            AUDIT_RECORDS = loadStoredAuditData();
            populateAuditDateSelect();

            const container = document.getElementById('wdoChartContainer');
            if (!container) return;

            if (typeof LightweightCharts === 'undefined') {{
                const fb = document.getElementById('chartFallback');
                if (fb) {{
                    fb.classList.remove('hidden');
                    fb.innerText = 'Visualizador TradingView carregando ou operando offline. Utilize os dados numéricos abaixo.';
                }}
                if (AUDIT_RECORDS.length > 0) {{
                    onAuditDateSelected(AUDIT_RECORDS[0].date);
                }}
                return;
            }}

            container.innerHTML = '';
            wdoChart = LightweightCharts.createChart(container, {{
                width: container.clientWidth || 800,
                height: 380,
                layout: {{
                    background: {{ color: '#070a10' }},
                    textColor: '#94a3b8',
                }},
                grid: {{
                    vertLines: {{ color: '#1e293b' }},
                    horzLines: {{ color: '#1e293b' }},
                }},
                crosshair: {{
                    mode: LightweightCharts.CrosshairMode.Normal,
                }},
                rightPriceScale: {{
                    borderColor: '#334155',
                    scaleMargins: {{ top: 0.15, bottom: 0.15 }},
                }},
                timeScale: {{
                    borderColor: '#334155',
                    timeVisible: true,
                    secondsVisible: false,
                }},
            }});

            candleSeries = wdoChart.addCandlestickSeries({{
                upColor: '#10b981',
                downColor: '#f43f5e',
                borderDownColor: '#f43f5e',
                borderUpColor: '#10b981',
                wickDownColor: '#f43f5e',
                wickUpColor: '#10b981',
            }});

            window.addEventListener('resize', () => {{
                if (wdoChart && container) {{
                    wdoChart.applyOptions({{ width: container.clientWidth }});
                }}
            }});

            updateLineButtonStyles();

            if (AUDIT_RECORDS.length > 0) {{
                onAuditDateSelected(AUDIT_RECORDS[0].date);
            }}
        }}

        function generateIntradayBars(record, tf) {{
            const w = record.wdo || {{}};
            const o = parseFloat(w.open || w.base_price_val || 5079.0);
            const h = parseFloat(w.high || 5115.0);
            const l = parseFloat(w.low || 5072.0);
            const c = parseFloat(w.close || 5080.5);

            const stepMin = tf === '1m' ? 1 : (tf === '5m' ? 5 : (tf === '15m' ? 15 : 60));
            const totalBars = Math.floor(540 / stepMin); // 09:00 as 18:00 = 540 min

            const dateParts = record.date.split('-').map(Number);
            const yr = dateParts[0];
            const mo = dateParts[1];
            const da = dateParts[2];
            // 09:00 BRT corresponde a 12:00 UTC
            const baseTimeUtc = Date.UTC(yr, mo - 1, da, 12, 0, 0);

            // Gerador pseudo-aleatorio deterministico baseado na data
            let seed = 12345;
            for (let i = 0; i < record.date.length; i++) {{
                seed = ((seed << 5) - seed) + record.date.charCodeAt(i);
                seed |= 0;
            }}
            function rnd() {{
                seed = (seed * 9301 + 49297) % 233280;
                return seed / 233280;
            }}

            // Anchors baseados no comportamento real registrado no ProfitChart:
            // 09:00 Abertura ~5079-5080
            // 09:45 Teste ~5078
            // 10:30 Disparada compradora ~5095
            // 11:35 Maxima do dia ~5115 (Resistencia)
            // 12:15 Recuo ~5095
            // 12:45 Repique topo menor ~5108
            // 14:00 Afunilamento do triangulo ~5100
            // 15:30 Afunilamento ~5090
            // 16:30 Suporte ~5086
            // 17:45 Minima do dia ~5072 (Suporte de fundo)
            // 18:00 Fechamento ~5080.5
            const anchors = [
                {{ m: 0,   p: o }},
                {{ m: 45,  p: Math.min(o - 1.0, (o + l) / 2) }},
                {{ m: 90,  p: o + (h - o) * 0.45 }},
                {{ m: 155, p: h }},                         // 11:35 Maxima do dia
                {{ m: 195, p: o + (h - o) * 0.45 }},        // 12:15 Recuo
                {{ m: 225, p: o + (h - o) * 0.80 }},        // 12:45 Topo menor
                {{ m: 300, p: o + (h - o) * 0.58 }},        // 14:00 Triangulo
                {{ m: 390, p: o + (h - o) * 0.30 }},        // 15:30 Fim triangulo
                {{ m: 450, p: o + (h - o) * 0.18 }},        // 16:30 Suporte
                {{ m: 520, p: l }},                         // 17:40 Minima do dia
                {{ m: 540, p: c }}                          // 18:00 Fechamento
            ];

            function getTargetPriceAtMinute(minute) {{
                if (minute <= anchors[0].m) return anchors[0].p;
                if (minute >= anchors[anchors.length - 1].m) return anchors[anchors.length - 1].p;
                for (let k = 0; k < anchors.length - 1; k++) {{
                    if (minute >= anchors[k].m && minute <= anchors[k + 1].m) {{
                        const frac = (minute - anchors[k].m) / (anchors[k + 1].m - anchors[k].m);
                        return anchors[k].p + (anchors[k + 1].p - anchors[k].p) * frac;
                    }}
                }}
                return c;
            }}

            const bars = [];
            let prevClose = o;

            for (let i = 0; i < totalBars; i++) {{
                const barMinute = i * stepMin;
                const barTimeSec = Math.floor((baseTimeUtc + barMinute * 60 * 1000) / 1000);
                const target = getTargetPriceAtMinute(barMinute);

                const noise = (rnd() - 0.5) * (tf === '1m' ? 1.2 : (tf === '5m' ? 2.2 : 3.5));
                let barClose = (i === totalBars - 1) ? c : (target + noise);
                barClose = Math.min(h, Math.max(l, barClose));
                let barOpen = (i === 0) ? o : prevClose;

                let barHigh = Math.max(barOpen, barClose) + rnd() * (tf === '1m' ? 1.0 : 2.0);
                let barLow = Math.min(barOpen, barClose) - rnd() * (tf === '1m' ? 1.0 : 2.0);

                barHigh = Math.min(h, Math.max(barHigh, Math.max(barOpen, barClose)));
                barLow = Math.max(l, Math.min(barLow, Math.min(barOpen, barClose)));

                bars.push({{
                    time: barTimeSec,
                    open: parseFloat(barOpen.toFixed(1)),
                    high: parseFloat(barHigh.toFixed(1)),
                    low: parseFloat(barLow.toFixed(1)),
                    close: parseFloat(barClose.toFixed(1))
                }});

                prevClose = barClose;
            }}

            // Garantir que a maxima e minima reais aparecam nos candles correspondentes
            let maxFound = -Infinity, minFound = Infinity, maxIdx = 0, minIdx = 0;
            bars.forEach((b, idx) => {{
                if (b.high > maxFound) {{ maxFound = b.high; maxIdx = idx; }}
                if (b.low < minFound) {{ minFound = b.low; minIdx = idx; }}
            }});
            bars[maxIdx].high = h;
            bars[minIdx].low = l;

            return bars;
        }}

        function switchChartTimeframe(tf) {{
            CURRENT_TIMEFRAME = tf;
            const tfs = ['1m', '5m', '15m', '1h', 'D'];
            tfs.forEach(t => {{
                const btn = document.getElementById('tfBtn_' + t);
                if (btn) {{
                    if (t === tf) {{
                        btn.className = 'px-2.5 py-1 text-xs rounded-lg font-black font-mono transition bg-amber-500 text-slate-950 shadow-md cursor-pointer border border-transparent';
                    }} else {{
                        btn.className = 'px-2.5 py-1 text-xs rounded-lg font-bold font-mono transition bg-slate-900 text-slate-400 hover:text-white border border-slate-800 cursor-pointer';
                    }}
                }}
            }});

            const sel = document.getElementById('auditDateSelect');
            const dateStr = sel ? sel.value : (AUDIT_RECORDS[0]?.date);
            renderChartForCurrentTimeframe(dateStr);
        }}

        function getStoredProfitCandles(dateStr) {{
            try {{
                const stored = localStorage.getItem('RADAR_PROFIT_CANDLES_' + dateStr);
                if (stored) {{
                    const parsed = JSON.parse(stored);
                    if (Array.isArray(parsed) && parsed.length > 0) return parsed;
                }}
            }} catch(e) {{}}
            return null;
        }}

        function aggregateBars(bars1m, periodMin) {{
            if (periodMin <= 1) return bars1m;
            const periodSec = periodMin * 60;
            const agg = [];
            let cur = null;

            bars1m.forEach(b => {{
                const bucketTime = Math.floor(b.time / periodSec) * periodSec;
                if (!cur || cur.time !== bucketTime) {{
                    if (cur) agg.push(cur);
                    cur = {{
                        time: bucketTime,
                        open: b.open,
                        high: b.high,
                        low: b.low,
                        close: b.close
                    }};
                }} else {{
                    cur.high = Math.max(cur.high, b.high);
                    cur.low = Math.min(cur.low, b.low);
                    cur.close = b.close;
                }}
            }});
            if (cur) agg.push(cur);
            return agg;
        }}

        function handleProfitDragOver(e) {{
            e.preventDefault();
            e.stopPropagation();
            const zone = document.getElementById('profitDropZone');
            if (zone) {{
                zone.classList.add('border-amber-400', 'bg-amber-500/10');
            }}
        }}

        function handleProfitDragLeave(e) {{
            e.preventDefault();
            e.stopPropagation();
            const zone = document.getElementById('profitDropZone');
            if (zone) {{
                zone.classList.remove('border-amber-400', 'bg-amber-500/10');
            }}
        }}

        function handleProfitFileDrop(e) {{
            e.preventDefault();
            e.stopPropagation();
            const zone = document.getElementById('profitDropZone');
            if (zone) {{
                zone.classList.remove('border-amber-400', 'bg-amber-500/10');
            }}
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {{
                processProfitFile(e.dataTransfer.files[0]);
            }}
        }}

        function handleProfitFileSelect(e) {{
            if (e.target && e.target.files && e.target.files.length > 0) {{
                processProfitFile(e.target.files[0]);
            }}
        }}

        function processProfitFile(file) {{
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(evt) {{
                const text = evt.target.result;
                parseAndApplyProfitData(text, file.name);
            }};
            reader.readAsText(file, "UTF-8");
        }}

        function parseProfitNumber(valStr) {{
            if (valStr === undefined || valStr === null) return NaN;
            let s = valStr.toString().trim();
            if (!s) return NaN;
            if (s.includes(',') && s.includes('.')) {{
                s = s.replace(/\\./g, '').replace(',', '.');
            }} else if (s.includes(',')) {{
                s = s.replace(',', '.');
            }}
            return parseFloat(s);
        }}

        function parseProfitDateTime(dateStr, timeStr) {{
            let dStr = (dateStr || '').trim();
            let tStr = (timeStr || '').trim();

            if (dStr.includes(' ')) {{
                const parts = dStr.split(' ');
                dStr = parts[0];
                if (!tStr && parts[1]) tStr = parts[1];
            }}
            if (!tStr) tStr = "09:00:00";

            let day = 1, month = 1, year = 2026;
            if (dStr.includes('/')) {{
                const dp = dStr.split('/').map(Number);
                day = dp[0];
                month = dp[1];
                year = dp[2] < 100 ? (2000 + dp[2]) : dp[2];
            }} else if (dStr.includes('-')) {{
                const dp = dStr.split('-').map(Number);
                if (dp[0] > 1000) {{
                    year = dp[0]; month = dp[1]; day = dp[2];
                }} else {{
                    day = dp[0]; month = dp[1]; year = dp[2];
                }}
            }}

            const tp = tStr.split(':').map(Number);
            const hour = tp[0] || 0;
            const min = tp[1] || 0;
            const sec = tp[2] || 0;

            const utcSec = Math.floor(Date.UTC(year, month - 1, day, hour + 3, min, sec) / 1000);
            const isoDate = `${{year}}-${{String(month).padStart(2, '0')}}-${{String(day).padStart(2, '0')}}`;
            return {{ utcSec, isoDate }};
        }}

        function parseAndApplyProfitData(text, fileName) {{
            if (!text || text.length < 10) {{
                alert("O arquivo selecionado está vazio ou ilegível.");
                return;
            }}

            const rawLines = text.split(/\\r?\\n/).map(l => l.trim()).filter(l => l.length > 0);
            if (rawLines.length < 2) {{
                alert("O arquivo não contém linhas suficientes de candles.");
                return;
            }}

            let delim = ';';
            const firstLine = rawLines[0];
            if (firstLine.includes(';')) delim = ';';
            else if (firstLine.includes('\\t')) delim = '\\t';
            else if (firstLine.includes(',')) delim = ',';

            let colDate = -1, colTime = -1, colOpen = -1, colHigh = -1, colLow = -1, colClose = -1;
            let dataStartIdx = 0;

            const headerCols = firstLine.split(delim).map(c => c.trim().toLowerCase());
            const hasHeader = headerCols.some(c => c.includes('data') || c.includes('date') || c.includes('abert') || c.includes('open') || c.includes('fech'));

            if (hasHeader) {{
                dataStartIdx = 1;
                headerCols.forEach((col, idx) => {{
                    if (col.includes('data') || col.includes('date')) {{
                        if (col.includes('hora') || col.includes('time')) {{
                            colDate = idx; colTime = idx;
                        }} else if (colDate === -1) {{
                            colDate = idx;
                        }}
                    }} else if (col.includes('hora') || col.includes('time')) {{
                        colTime = idx;
                    }} else if (col.includes('abert') || col.includes('open') || col === 'abe') {{
                        colOpen = idx;
                    }} else if (col.includes('max') || col.includes('high')) {{
                        colHigh = idx;
                    }} else if (col.includes('min') || col.includes('low')) {{
                        colLow = idx;
                    }} else if (col.includes('fech') || col.includes('close') || col.includes('ult') || col === 'fch') {{
                        colClose = idx;
                    }}
                }});
            }}

            if (colOpen === -1 || colHigh === -1 || colLow === -1 || colClose === -1) {{
                const testCols = rawLines[dataStartIdx].split(delim);
                const firstIsTicker = isNaN(parseFloat(testCols[0])) && !testCols[0].includes('/') && !testCols[0].includes('-');
                const offset = firstIsTicker ? 1 : 0;
                
                const colAfterDate = testCols[offset + 1] || "";
                const hasSeparateTimeCol = colAfterDate.includes(':');

                if (hasSeparateTimeCol) {{
                    colDate = offset;
                    colTime = offset + 1;
                    colOpen = offset + 2;
                    colHigh = offset + 3;
                    colLow = offset + 4;
                    colClose = offset + 5;
                }} else {{
                    colDate = offset;
                    colTime = -1;
                    colOpen = offset + 1;
                    colHigh = offset + 2;
                    colLow = offset + 3;
                    colClose = offset + 4;
                }}
            }}

            const parsedBars = [];
            let detectedIsoDate = "";

            for (let i = dataStartIdx; i < rawLines.length; i++) {{
                const cols = rawLines[i].split(delim);
                if (cols.length < 4) continue;

                const dStr = cols[colDate] || "";
                const tStr = (colTime !== -1 && colTime !== colDate) ? cols[colTime] : "";
                const dt = parseProfitDateTime(dStr, tStr);

                const o = parseProfitNumber(cols[colOpen]);
                const h = parseProfitNumber(cols[colHigh]);
                const l = parseProfitNumber(cols[colLow]);
                const c = parseProfitNumber(cols[colClose]);

                if (isNaN(o) || isNaN(h) || isNaN(l) || isNaN(c)) continue;
                if (!detectedIsoDate && dt.isoDate) detectedIsoDate = dt.isoDate;

                parsedBars.push({{
                    time: dt.utcSec,
                    open: o,
                    high: h,
                    low: l,
                    close: c
                }});
            }}

            if (parsedBars.length === 0) {{
                alert("Não foi possível extrair candles válidos do arquivo. Verifique o formato exportado pelo Profit.");
                return;
            }}

            parsedBars.sort((a, b) => a.time - b.time);
            const uniqueBars = [];
            const seenTimes = new Set();
            parsedBars.forEach(b => {{
                if (!seenTimes.has(b.time)) {{
                    seenTimes.add(b.time);
                    uniqueBars.push(b);
                }}
            }});

            const targetDate = detectedIsoDate || (document.getElementById('auditDateSelect')?.value) || '2026-10-16';
            localStorage.setItem('RADAR_PROFIT_CANDLES_' + targetDate, JSON.stringify(uniqueBars));

            const sessionHigh = Math.max(...uniqueBars.map(b => b.high));
            const sessionLow = Math.min(...uniqueBars.map(b => b.low));
            const sessionClose = uniqueBars[uniqueBars.length - 1].close;
            const sessionOpen = uniqueBars[0].open;

            let record = AUDIT_RECORDS.find(r => r.date === targetDate);
            if (!record) {{
                record = {{
                    date: targetDate,
                    win: {{ bias: 'ALTA', expected_pct: '+0.4% a +1.0%' }},
                    wdo: {{ bias: 'BAIXA', expected_pct: '-0.8% a -0.3%', base_price_val: sessionOpen }}
                }};
                AUDIT_RECORDS.unshift(record);
                populateAuditDateSelect();
            }}
            if (!record.wdo) record.wdo = {{}};
            record.wdo.high = sessionHigh;
            record.wdo.low = sessionLow;
            record.wdo.close = sessionClose;
            record.wdo.open = sessionOpen;
            record.wdo.has_profit_file = true;

            saveStoredAuditData(AUDIT_RECORDS);

            const sel = document.getElementById('auditDateSelect');
            if (sel) sel.value = targetDate;

            const inpH = document.getElementById('inpAuditHigh');
            if (inpH) inpH.value = sessionHigh.toFixed(1);
            const inpL = document.getElementById('inpAuditLow');
            if (inpL) inpL.value = sessionLow.toFixed(1);
            const inpC = document.getElementById('inpAuditClose');
            if (inpC) inpC.value = sessionClose.toFixed(1);

            const statusBadge = document.getElementById('profitLoadedStatus');
            if (statusBadge) {{
                statusBadge.innerText = '✔ ' + uniqueBars.length + ' candles reais (' + targetDate + ')';
                statusBadge.classList.remove('hidden');
            }}

            renderChartForCurrentTimeframe(targetDate);
            onAuditValuesChanged();

            const toast = document.getElementById('auditToastMsg');
            const toastTxt = document.getElementById('auditToastText');
            if (toast && toastTxt) {{
                toastTxt.innerText = '✔ ' + uniqueBars.length + ' candles do ProfitChart importados com sucesso! Máx: ' + sessionHigh.toFixed(1) + ' | Mín: ' + sessionLow.toFixed(1) + ' | Fch: ' + sessionClose.toFixed(1);
                toast.classList.remove('hidden');
                setTimeout(() => toast.classList.add('hidden'), 5000);
            }}
        }}

        function renderChartForCurrentTimeframe(dateStr) {{
            if (!candleSeries || typeof LightweightCharts === 'undefined' || !wdoChart) return;
            const record = AUDIT_RECORDS.find(r => r.date === dateStr) || AUDIT_RECORDS[0];
            if (!record) return;

            if (CURRENT_TIMEFRAME === 'D') {{
                wdoChart.applyOptions({{
                    timeScale: {{ timeVisible: false, secondsVisible: false }}
                }});
                const sorted = [...AUDIT_RECORDS].sort((a, b) => a.date.localeCompare(b.date));
                const dailyBars = sorted.map(r => {{
                    const w = r.wdo || {{}};
                    const o = parseFloat(w.open || w.base_price_val || 5080.5);
                    const h = parseFloat(w.high || o + 10);
                    const l = parseFloat(w.low || o - 10);
                    const c = parseFloat(w.close || o);
                    return {{ time: r.date, open: o, high: h, low: l, close: c }};
                }});
                candleSeries.setData(dailyBars);
            }} else {{
                wdoChart.applyOptions({{
                    timeScale: {{ timeVisible: true, secondsVisible: false }}
                }});
                const storedReal = getStoredProfitCandles(record.date);
                let intradayBars;
                if (storedReal && storedReal.length > 0) {{
                    const periodMin = CURRENT_TIMEFRAME === '1m' ? 1 : (CURRENT_TIMEFRAME === '5m' ? 5 : (CURRENT_TIMEFRAME === '15m' ? 15 : 60));
                    intradayBars = aggregateBars(storedReal, periodMin);
                }} else {{
                    intradayBars = generateIntradayBars(record, CURRENT_TIMEFRAME);
                }}
                candleSeries.setData(intradayBars);
            }}

            wdoChart.timeScale().fitContent();
            updateChartPriceLines(record.wdo || {{}});
        }}

        function toggleChartLine(lineKey) {{
            VISIBLE_LINES[lineKey] = !VISIBLE_LINES[lineKey];
            updateLineButtonStyles();

            const sel = document.getElementById('auditDateSelect');
            const dateStr = sel ? sel.value : (AUDIT_RECORDS[0]?.date);
            const record = AUDIT_RECORDS.find(r => r.date === dateStr) || AUDIT_RECORDS[0];
            if (record) {{
                updateChartPriceLines(record.wdo || {{}});
            }}
        }}

        function updateLineButtonStyles() {{
            const btnBase = document.getElementById('btnToggleBase');
            if (btnBase) {{
                if (VISIBLE_LINES.base) {{
                    btnBase.className = 'px-2.5 py-1 rounded-lg bg-slate-800 text-white border-2 border-slate-300 shadow-sm transition active:scale-95 flex items-center gap-1.5 cursor-pointer opacity-100';
                }} else {{
                    btnBase.className = 'px-2.5 py-1 rounded-lg bg-slate-950 text-slate-500 border border-slate-800 transition active:scale-95 flex items-center gap-1.5 cursor-pointer opacity-40 line-through';
                }}
            }}

            const btnT1 = document.getElementById('btnToggleT1');
            if (btnT1) {{
                if (VISIBLE_LINES.t1) {{
                    btnT1.className = 'px-2.5 py-1 rounded-lg bg-sky-500/20 text-sky-300 border-2 border-sky-400 shadow-sm shadow-sky-500/20 transition active:scale-95 flex items-center gap-1.5 cursor-pointer opacity-100';
                }} else {{
                    btnT1.className = 'px-2.5 py-1 rounded-lg bg-slate-950 text-slate-500 border border-slate-800 transition active:scale-95 flex items-center gap-1.5 cursor-pointer opacity-40 line-through';
                }}
            }}

            const btnT2 = document.getElementById('btnToggleT2');
            if (btnT2) {{
                if (VISIBLE_LINES.t2) {{
                    btnT2.className = 'px-2.5 py-1 rounded-lg bg-purple-500/20 text-purple-300 border-2 border-purple-400 shadow-sm shadow-purple-500/20 transition active:scale-95 flex items-center gap-1.5 cursor-pointer opacity-100';
                }} else {{
                    btnT2.className = 'px-2.5 py-1 rounded-lg bg-slate-950 text-slate-500 border border-slate-800 transition active:scale-95 flex items-center gap-1.5 cursor-pointer opacity-40 line-through';
                }}
            }}
        }}

        function updateChartPriceLines(w) {{
            if (!candleSeries || typeof LightweightCharts === 'undefined') return;
            priceLines.forEach(l => {{
                try {{ candleSeries.removePriceLine(l); }} catch(e) {{}}
            }});
            priceLines = [];

            if (VISIBLE_LINES.base && w.base_price_val) {{
                priceLines.push(candleSeries.createPriceLine({{
                    price: w.base_price_val,
                    color: '#e2e8f0',
                    lineWidth: 1,
                    lineStyle: LightweightCharts.LineStyle.Dotted,
                    axisLabelVisible: true,
                    title: 'Ponto Zero (' + w.base_price_val.toFixed(1) + ')',
                }}));
            }}
            if (VISIBLE_LINES.t1 && w.line_t1_val) {{
                priceLines.push(candleSeries.createPriceLine({{
                    price: w.line_t1_val,
                    color: '#38bdf8',
                    lineWidth: 2,
                    lineStyle: LightweightCharts.LineStyle.Dashed,
                    axisLabelVisible: true,
                    title: 'Alvo 1 (' + w.line_t1_val.toFixed(1) + ')',
                }}));
            }}
            if (VISIBLE_LINES.t2 && w.line_t2_val) {{
                priceLines.push(candleSeries.createPriceLine({{
                    price: w.line_t2_val,
                    color: '#c084fc',
                    lineWidth: 2,
                    lineStyle: LightweightCharts.LineStyle.Dashed,
                    axisLabelVisible: true,
                    title: 'Alvo 2 (' + w.line_t2_val.toFixed(1) + ')',
                }}));
            }}
        }}

        function populateAuditDateSelect() {{
            const sel = document.getElementById('auditDateSelect');
            if (!sel) return;
            sel.innerHTML = '';
            AUDIT_RECORDS.forEach(r => {{
                const opt = document.createElement('option');
                opt.value = r.date;
                opt.innerText = r.date + ' (' + (r.wdo?.bias || 'WDO') + ')';
                sel.appendChild(opt);
            }});
        }}

        function onAuditDateSelected(dateStr) {{
            const record = AUDIT_RECORDS.find(r => r.date === dateStr) || AUDIT_RECORDS[0];
            if (!record) return;

            const w = record.wdo || {{}};
            
            const pBadge = document.getElementById('projDateBadge');
            if (pBadge) pBadge.innerText = record.date;
            const pBias = document.getElementById('projBiasText');
            if (pBias) {{
                pBias.innerText = w.bias || '--';
                pBias.className = 'font-bold text-sm ' + (w.bias === 'BAIXA' ? 'text-rose-400' : (w.bias === 'ALTA' ? 'text-emerald-400' : 'text-amber-400'));
            }}
            const pRange = document.getElementById('projRangeText');
            if (pRange) pRange.innerText = (w.expected_pct || '--') + ' (' + (w.points_range || '--') + ')';
            const pBase = document.getElementById('projBaseText');
            if (pBase) pBase.innerText = (w.base_price_val || 5080.5).toFixed(1) + ' pts';
            const pT1 = document.getElementById('projT1Text');
            if (pT1) pT1.innerText = (w.line_t1_val || 5065.5).toFixed(1) + ' pts (' + (w.pts_t1 || '-15.0 pts') + ')';
            const pT2 = document.getElementById('projT2Text');
            if (pT2) pT2.innerText = (w.line_t2_val || 5040.0).toFixed(1) + ' pts (' + (w.pts_t2 || '-40.5 pts') + ')';

            const lblBase = document.getElementById('lblChartBase');
            if (lblBase) lblBase.innerText = (w.base_price_val || 5080.5).toFixed(1);
            const lblT1 = document.getElementById('lblChartT1');
            if (lblT1) lblT1.innerText = (w.line_t1_val || 5065.5).toFixed(1);
            const lblT2 = document.getElementById('lblChartT2');
            if (lblT2) lblT2.innerText = (w.line_t2_val || 5040.0).toFixed(1);

            const inpH = document.getElementById('inpAuditHigh');
            if (inpH) inpH.value = parseFloat(w.high || 5115.0).toFixed(1);
            const inpL = document.getElementById('inpAuditLow');
            if (inpL) inpL.value = parseFloat(w.low || 5072.0).toFixed(1);
            const inpC = document.getElementById('inpAuditClose');
            if (inpC) inpC.value = parseFloat(w.close || 5080.5).toFixed(1);

            const storedReal = getStoredProfitCandles(record.date);
            const statusBadge = document.getElementById('profitLoadedStatus');
            if (statusBadge) {{
                if (storedReal && storedReal.length > 0) {{
                    statusBadge.innerText = '✔ ' + storedReal.length + ' candles reais (' + record.date + ')';
                    statusBadge.classList.remove('hidden');
                }} else {{
                    statusBadge.classList.add('hidden');
                }}
            }}

            updateAuditedButtonDisplay(w.is_audited);
            renderChartForCurrentTimeframe(record.date);
            onAuditValuesChanged();
        }}

        function onAuditValuesChanged() {{
            const sel = document.getElementById('auditDateSelect');
            const dateStr = sel ? sel.value : (AUDIT_RECORDS[0]?.date);
            const record = AUDIT_RECORDS.find(r => r.date === dateStr);
            if (!record) return;

            const w = record.wdo || {{}};
            const high = parseFloat(document.getElementById('inpAuditHigh')?.value || w.high || 0);
            const low = parseFloat(document.getElementById('inpAuditLow')?.value || w.low || 0);
            const close = parseFloat(document.getElementById('inpAuditClose')?.value || w.close || 0);

            const isDown = w.bias === 'BAIXA';
            const t1 = w.line_t1_val || (isDown ? (w.base_price_val - 15) : (w.base_price_val + 15));
            const t2 = w.line_t2_val || (isDown ? (w.base_price_val - 40.5) : (w.base_price_val + 40.5));

            const hitT1 = isDown ? (low <= t1) : (high >= t1);
            const elT1 = document.getElementById('auditChkTarget1');
            if (elT1) {{
                elT1.innerHTML = hitT1 ? '<span class="text-emerald-400 font-bold">✔ ATINGIDO (' + (isDown ? 'Mín ' + low.toFixed(1) + ' ≤ ' + t1.toFixed(1) : 'Máx ' + high.toFixed(1) + ' ≥ ' + t1.toFixed(1)) + ')</span>' : '<span class="text-slate-500 font-bold">✖ Não atingiu</span>';
            }}

            const hitT2 = isDown ? (low <= t2) : (high >= t2);
            const elT2 = document.getElementById('auditChkTarget2');
            if (elT2) {{
                elT2.innerHTML = hitT2 ? '<span class="text-emerald-400 font-bold">✔ ATINGIDO (' + (isDown ? 'Mín ' + low.toFixed(1) + ' ≤ ' + t2.toFixed(1) : 'Máx ' + high.toFixed(1) + ' ≥ ' + t2.toFixed(1)) + ')</span>' : '<span class="text-slate-500 font-bold">✖ Não atingiu</span>';
            }}

            const base = w.base_price_val || 5080.5;
            const diffPct = ((close - base) / base) * 100;
            const hitRange = isDown ? (diffPct <= -0.20 && diffPct >= -1.2) : (diffPct >= 0.20 && diffPct <= 1.2);
            const elRange = document.getElementById('auditChkRange');
            if (elRange) {{
                elRange.innerHTML = hitRange ? '<span class="text-emerald-400 font-bold">✔ DENTRO DA FAIXA (' + (diffPct >= 0 ? '+' : '') + diffPct.toFixed(2) + '%)</span>' : '<span class="text-amber-400 font-bold">● Variação: ' + (diffPct >= 0 ? '+' : '') + diffPct.toFixed(2) + '%</span>';
            }}
        }}

        function toggleDayAuditedStatus() {{
            const sel = document.getElementById('auditDateSelect');
            const dateStr = sel ? sel.value : (AUDIT_RECORDS[0]?.date);
            const record = AUDIT_RECORDS.find(r => r.date === dateStr);
            if (!record) return;

            if (!record.wdo) record.wdo = {{}};
            record.wdo.is_audited = !record.wdo.is_audited;

            saveStoredAuditData(AUDIT_RECORDS);
            updateAuditedButtonDisplay(record.wdo.is_audited);

            const toast = document.getElementById('auditToastMsg');
            const toastTxt = document.getElementById('auditToastText');
            if (toast && toastTxt) {{
                if (record.wdo.is_audited) {{
                    toastTxt.innerText = '✔ Pregão ' + dateStr + ' validado e conferido pelo trader!';
                }} else {{
                    toastTxt.innerText = 'Pregão ' + dateStr + ': conferência desmarcada.';
                }}
                toast.classList.remove('hidden');
                setTimeout(() => toast.classList.add('hidden'), 3500);
            }}
        }}

        function updateAuditedButtonDisplay(isAudited) {{
            const btn = document.getElementById('btnMarkAudited');
            const lbl = document.getElementById('lblMarkAudited');
            if (!btn || !lbl) return;

            if (isAudited) {{
                btn.className = 'px-2.5 py-0.5 rounded-lg text-[11px] font-bold bg-emerald-500/25 text-emerald-300 border border-emerald-500/50 shadow-sm shadow-emerald-500/20 transition cursor-pointer flex items-center gap-1';
                lbl.innerHTML = '✔ Conferido pelo Trader';
            }} else {{
                btn.className = 'px-2.5 py-0.5 rounded-lg text-[11px] font-bold bg-slate-900 text-slate-400 hover:text-white border border-slate-700 transition cursor-pointer flex items-center gap-1';
                lbl.innerHTML = 'Marcar como Conferido';
            }}
        }}

        function saveCurrentAuditDay() {{
            const sel = document.getElementById('auditDateSelect');
            const dateStr = sel ? sel.value : (AUDIT_RECORDS[0]?.date);
            const record = AUDIT_RECORDS.find(r => r.date === dateStr);
            if (!record) return;

            const w = record.wdo || {{}};
            const high = parseFloat(document.getElementById('inpAuditHigh')?.value || w.high);
            const low = parseFloat(document.getElementById('inpAuditLow')?.value || w.low);
            const close = parseFloat(document.getElementById('inpAuditClose')?.value || w.close);

            w.high = high;
            w.low = low;
            w.close = close;

            const isDown = w.bias === 'BAIXA';
            const t1 = w.line_t1_val || 5065.5;
            const t2 = w.line_t2_val || 5040.0;
            const base = w.base_price_val || 5080.5;

            w.t1_hit = isDown ? (low <= t1) : (high >= t1);
            w.t2_hit = isDown ? (low <= t2) : (high >= t2);
            const diffPct = ((close - base) / base) * 100;
            w.actual_pct = (diffPct >= 0 ? '+' : '') + diffPct.toFixed(2) + '%';
            w.range_hit = isDown ? (diffPct <= -0.20 && diffPct >= -1.2) : (diffPct >= 0.20 && diffPct <= 1.2);

            saveStoredAuditData(AUDIT_RECORDS);
            renderChartForCurrentTimeframe(dateStr);

            const toast = document.getElementById('auditToastMsg');
            const toastTxt = document.getElementById('auditToastText');
            if (toast && toastTxt) {{
                toastTxt.innerText = '✔ Pregão ' + dateStr + ' auditado com sucesso! Dados reais salvos e integrados ao histórico.';
                toast.classList.remove('hidden');
                setTimeout(() => toast.classList.add('hidden'), 4000);
            }}
        }}

        function copyAuditDaySummary() {{
            const sel = document.getElementById('auditDateSelect');
            const dateStr = sel ? sel.value : (AUDIT_RECORDS[0]?.date);
            const record = AUDIT_RECORDS.find(r => r.date === dateStr);
            if (!record) return;

            const w = record.wdo || {{}};
            const text = `📋 AUDITORIA DO PREGÃO WDO (${{dateStr}})\\n\\n🔮 PROJEÇÃO DO RADAR (08:20):\\n• Viés: ${{w.bias}} (${{w.expected_pct || ''}})\\n• Ponto Zero: ${{w.base_price_val || 5080.5}} pts\\n• Alvo 1: ${{w.line_t1_val || 5065.5}} pts\\n• Alvo 2: ${{w.line_t2_val || 5040.0}} pts\\n\\n🎯 O QUE ACONTECEU NO PROFITCHART:\\n• Máxima: ${{w.high || ''}} pts\\n• Mínima: ${{w.low || ''}} pts\\n• Fechamento: ${{w.close || ''}} pts (${{w.actual_pct || ''}})\\n• Alvo 1: ${{w.t1_hit ? '✔ Atingido' : '✖ Não atingido'}}\\n• Alvo 2: ${{w.t2_hit ? '✔ Atingido' : '✖ Não atingido'}}\\n• Fechamento na Faixa: ${{w.range_hit ? '✔ Na Faixa' : '✖ Fora'}}\\n• Conferência: ${{w.is_audited ? '✔ Validado pelo Trader' : 'Pendente'}}`;

            navigator.clipboard.writeText(text).then(() => {{
                alert('✔ Resumo da auditoria copiado para a área de transferência!');
            }});
        }}

        function exportAuditDatasetJson() {{
            const blob = new Blob([JSON.stringify(AUDIT_RECORDS, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'history_auditado_wdo.json';
            a.click();
            URL.revokeObjectURL(url);
        }}

        setInterval(updateClockAndSessions, 1000);
        setInterval(fetchLiveBtc, 15000);
        setInterval(fetchLiveForex, 30000);

        document.addEventListener('DOMContentLoaded', () => {{
            refreshLiveMarket();
            initAuditChart();
        }});
    </script>

</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path
