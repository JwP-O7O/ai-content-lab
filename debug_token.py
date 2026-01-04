import os
from dotenv import load_dotenv
from github import Github

load_dotenv()
token = os.getenv("GITHUB_TOKEN")

print(f"--- TOKEN INSPECTIE ---")
if not token:
    print("❌ FOUT: Geen token gevonden in .env!")
else:
    # Laat alleen de eerste 4 letters zien voor veiligheid
    print(f"✅ Token gevonden: {token[:4]}... (Lengte: {len(token)})")
    
    print("🔄 Testen van verbinding met GitHub...")
    try:
        g = Github(token)
        user = g.get_user()
        print(f"🎉 SUCCES! Verbonden als: {user.login}")
    except Exception as e:
        print(f"❌ MISLUKT: {e}")
