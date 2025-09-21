#!/usr/bin/env python3
"""
Скрипт для анализа неиспользуемых импортов в проекте.
"""

import ast
import os
from pathlib import Path
from typing import Set, Dict, List


class ImportAnalyzer:
    """Анализатор импортов для поиска неиспользуемых."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.unused_imports = {}
        
    def analyze_file(self, file_path: Path) -> Dict[str, List[str]]:
        """Анализировать один файл на предмет неиспользуемых импортов."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Собираем все импорты
            imports = set()
            import_froms = set()
            
            # Собираем все используемые имена
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            import_froms.add(alias.name)
                elif isinstance(node, ast.Name):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # Для атрибутов типа module.function
                    if isinstance(node.value, ast.Name):
                        used_names.add(node.value.id)
            
            # Находим неиспользуемые импорты
            unused = []
            
            # Проверяем обычные импорты
            for imp in imports:
                if imp not in used_names:
                    unused.append(imp)
            
            # Проверяем импорты from
            for imp in import_froms:
                if imp not in used_names:
                    unused.append(imp)
            
            return {"unused": unused, "total": len(imports) + len(import_froms)}
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_project(self) -> Dict[str, Dict]:
        """Анализировать весь проект."""
        results = {}
        
        # Находим все Python файлы
        for py_file in self.project_root.rglob("*.py"):
            # Пропускаем __pycache__
            if "__pycache__" in str(py_file):
                continue
                
            # Пропускаем виртуальное окружение
            if "venv" in str(py_file) or "env" in str(py_file):
                continue
            
            relative_path = py_file.relative_to(self.project_root)
            result = self.analyze_file(py_file)
            results[str(relative_path)] = result
        
        return results
    
    def print_report(self):
        """Вывести отчет о неиспользуемых импортах."""
        print("🔍 Анализ неиспользуемых импортов...")
        print()
        
        results = self.analyze_project()
        
        total_files = 0
        files_with_unused = 0
        total_unused = 0
        
        for file_path, result in results.items():
            if "error" in result:
                print(f"❌ {file_path}: {result['error']}")
                continue
            
            total_files += 1
            
            if result["unused"]:
                files_with_unused += 1
                total_unused += len(result["unused"])
                print(f"⚠️  {file_path}:")
                for unused in result["unused"]:
                    print(f"   • {unused}")
                print()
        
        print(f"📊 Статистика:")
        print(f"   Всего файлов: {total_files}")
        print(f"   Файлов с неиспользуемыми импортами: {files_with_unused}")
        print(f"   Всего неиспользуемых импортов: {total_unused}")
        
        if files_with_unused == 0:
            print("🎉 Все импорты используются!")


if __name__ == "__main__":
    analyzer = ImportAnalyzer(".")
    analyzer.print_report()
