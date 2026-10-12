# -*- coding: utf-8 -*-
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_notification(analysis, dashboard_url=""):
    """Envia o resumo executivo matinal formatado direto no Telegram."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("ℹ️ Telegram não configurado (TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID ausentes). Pulando...")
        return False
        
    win = analysis["win"]
    wdo = analysis["wdo"]
    fp = analysis.get("flight_plan", {})
    risk_score = analysis.get("risk_score", 5)
    risk_label = analysis.get("risk_label", "Moderado")
    
    url_text = f"\n🔗 *Acessar Painel Completo:* {dashboard_url}" if dashboard_url else ""
    
    msg = f"""🎯 *RADAR DE ABERTURA B3 — DAY TRADE*

⚡ *PLANO DE VOO EM 30 SEGUNDOS:*
• *WIN:* {win.get('trend_badge', win['direction'])}
• *WDO:* {wdo.get('trend_badge', wdo['direction'])}
• *Risco:* {risk_score}/10 ({risk_label})

📊 *MINI-ÍNDICE (WIN):*
• Projeção: `{win['expected_range']}` ({win.get('points_range')})
• Alvo 1: `{win.get('target_1_val', win.get('target_1'))}`
• Alvo 2: `{win.get('target_2_val', win.get('target_2'))}`
• Trava Stop: `{win.get('trava_val', win.get('trava_risco'))}`

💵 *MINI-DÓLAR (WDO):*
• Projeção: `{wdo['expected_range']}` ({wdo.get('points_range')})
• Alvo 1: `{wdo.get('target_1_val', wdo.get('target_1'))}`
• Alvo 2: `{wdo.get('target_2_val', wdo.get('target_2'))}`
• Trava Stop: `{wdo.get('trava_val', wdo.get('trava_risco'))}`

⚠️ *ZONA DE PERIGO:*
{fp.get('danger', 'Atenção às 10:00 e 10:30.')}
{url_text}"""

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "Markdown"
        }
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print("✔ Alerta do Telegram enviado com sucesso!")
            return True
        else:
            print(f"⚠️ Erro ao enviar Telegram: {res.text}")
            return False
    except Exception as e:
        print(f"⚠️ Falha no envio do Telegram: {e}")
        return False

def send_email_notification(analysis, dashboard_url=""):
    """Envia o resumo por e-mail via API do Resend (gratuita e confiável)."""
    resend_key = os.getenv("RESEND_API_KEY")
    email_to = os.getenv("NOTIFICATION_EMAIL")
    
    if not resend_key or not email_to:
        print("ℹ️ E-mail não configurado (RESEND_API_KEY ou NOTIFICATION_EMAIL ausentes). Pulando...")
        return False
        
    win = analysis["win"]
    wdo = analysis["wdo"]
    fp = analysis.get("flight_plan", {})
    
    html_content = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, sans-serif; background-color: #0b0f17; color: #f1f5f9; padding: 24px; border-radius: 12px; max-width: 600px; margin: auto;">
        <h2 style="color: #f59e0b; margin-top: 0; font-size: 20px;">🎯 Radar de Abertura Day Trade B3</h2>
        
        <div style="background-color: #131b2a; border-left: 4px solid #f59e0b; padding: 14px; border-radius: 6px; margin-bottom: 20px;">
            <p style="margin: 0 0 6px 0; font-size: 13px;"><strong>📊 WIN:</strong> {win.get('trend_badge', win['direction'])}</p>
            <p style="margin: 0 0 6px 0; font-size: 13px;"><strong>💵 WDO:</strong> {wdo.get('trend_badge', wdo['direction'])}</p>
            <p style="margin: 0; font-size: 13px; color: #f87171;"><strong>⚠️ Perigo:</strong> {fp.get('danger')}</p>
        </div>

        <div style="background-color: #131b2a; padding: 16px; border-radius: 8px; margin-bottom: 16px; border: 1px solid #1e293b;">
            <h3 style="color: #10b981; margin: 0 0 10px 0; font-size: 15px;">📊 Mini-Índice (WIN)</h3>
            <p style="margin: 4px 0; font-size: 13px;">• Projeção: <strong>{win['expected_range']}</strong> ({win.get('points_range')})</p>
            <p style="margin: 4px 0; font-size: 13px;">• Alvo 1: <strong>{win.get('target_1_val')}</strong></p>
            <p style="margin: 4px 0; font-size: 13px;">• Alvo 2: <strong>{win.get('target_2_val')}</strong></p>
            <p style="margin: 4px 0; font-size: 13px; color: #f87171;">• Trava de Stop: <strong>{win.get('trava_val')}</strong></p>
        </div>

        <div style="background-color: #131b2a; padding: 16px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #1e293b;">
            <h3 style="color: #38bdf8; margin: 0 0 10px 0; font-size: 15px;">💵 Mini-Dólar (WDO)</h3>
            <p style="margin: 4px 0; font-size: 13px;">• Projeção: <strong>{wdo['expected_range']}</strong> ({wdo.get('points_range')})</p>
            <p style="margin: 4px 0; font-size: 13px;">• Alvo 1: <strong>{wdo.get('target_1_val')}</strong></p>
            <p style="margin: 4px 0; font-size: 13px;">• Alvo 2: <strong>{wdo.get('target_2_val')}</strong></p>
            <p style="margin: 4px 0; font-size: 13px; color: #f87171;">• Trava de Stop: <strong>{wdo.get('trava_val')}</strong></p>
        </div>

        {f'<div style="text-align: center; margin-top: 24px;"><a href="{dashboard_url}" style="background-color: #f59e0b; color: #0b0f17; font-weight: bold; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block;">Acessar Painel Interativo</a></div>' if dashboard_url else ''}
    </div>
    """
    
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json"
        }
        data = {
            "from": "Radar Day Trade <onboarding@resend.dev>",
            "to": [email_to],
            "subject": f"🎯 Radar Day Trade B3 - {win.get('trend_badge', win['direction'])} WIN | {wdo.get('trend_badge', wdo['direction'])} WDO",
            "html": html_content
        }
        res = requests.post(url, headers=headers, json=data, timeout=10)
        if res.status_code in [200, 201]:
            print("✔ E-mail enviado com sucesso via Resend!")
            return True
        else:
            print(f"⚠️ Erro ao enviar e-mail: {res.text}")
            return False
    except Exception as e:
        print(f"⚠️ Falha no envio de e-mail: {e}")
        return False

def notify_all(analysis, dashboard_url=""):
    """Dispara todas as notificações ativas (Telegram e E-mail)."""
    t_ok = send_telegram_notification(analysis, dashboard_url)
    e_ok = send_email_notification(analysis, dashboard_url)
    return t_ok or e_ok
