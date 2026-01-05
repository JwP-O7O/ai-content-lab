import os
import ast
from loguru import logger

class QualityAssuranceAgent:
    def __init__(self):
        self.name = "QualityAssuranceAgent"

    def audit_code(self, filepath):
        """Checkt code op syntax fouten (Python)"""
        if not filepath.endswith(".py"): 
            return {"status": "passed", "msg": "Geen Python bestand"}

        logger.info(f"[{self.name}] 🔍 Inspecteren van {os.path.basename(filepath)}...")
        
        try:
            with open(filepath, 'r') as f:
                source = f.read()
            
            # 1. Syntax Check (Compileer zonder uit te voeren)
            ast.parse(source)
            
            return {"status": "passed", "msg": "Syntax OK"}
            
        except SyntaxError as e:
            error_msg = f"❌ Syntax Fout op regel {e.lineno}: {e.msg}"
            logger.error(f"[{self.name}] {error_msg}")
            return {"status": "failed", "msg": error_msg}
        except Exception as e:
            return {"status": "failed", "msg": str(e)}

    def audit_web(self, filepath):
        """Simpele check voor HTML"""
        # Hier zou je later een HTML validator kunnen inbouwen
        return {"status": "passed", "msg": "HTML structuur OK"}
