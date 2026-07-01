import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import re
import os
import unicodedata
import zipfile
import tempfile
import itertools
import threading

# --- PALETA DE CORES (Versão Clean e Profissional) ---
BG_COLOR = "#0A1D3A"       
PANEL_BG = "#102F4D"       
FG_COLOR = "#4DD0E1"       
FG_TEXT = "#FFFFFF"        
FG_ALT = "#82B1FF"         
BTN_BG = "#133458"         
BTN_ACTIVE = "#1C4E80"     
WARN_COLOR = "#FF5252"     
OK_COLOR = "#69F0AE"       
FONT_HUD = ("Segoe UI", 10)
FONT_HUD_B = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")

class ProgressBarHUD(tk.Canvas):
    """Barra de Progresso Linear Profissional"""
    def __init__(self, parent, width=400, height=30, **kwargs):
        super().__init__(parent, width=width, height=height, bg=PANEL_BG, highlightthickness=1, highlightbackground=FG_COLOR, **kwargs)
        self.width = width
        self.height = height
        self.bar = self.create_rectangle(0, 0, 0, height, fill=FG_COLOR, outline="")
        self.text_info = self.create_text(width/2, height/2, text="Aguardando... 0%", fill=FG_TEXT, font=("Segoe UI", 10, "bold"))

    def update_progress(self, percent, status="Processando"):
        if percent > 100: percent = 100
        pix = (percent / 100) * self.width
        self.coords(self.bar, 0, 0, pix, self.height)
        cor_texto = BG_COLOR if percent > 50 else FG_TEXT
        self.itemconfig(self.text_info, text=f"{status} - {int(percent)}%", fill=cor_texto)

class SearchCRTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SearchCRT - Soluções em Dados")
        self.root.geometry("600x400")
        self.root.configure(bg=BG_COLOR, padx=20, pady=20)
        
        # --- Interface Principal ---
        self.lbl_titulo = tk.Label(root, text="SearchCRT", font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR)
        self.lbl_titulo.pack(pady=(0, 30))
        
        self.btn_comparativo = tk.Button(root, text="COMPARATIVO DE DADOS", command=self.abrir_comparativo, 
                                         width=40, height=3, font=FONT_HUD_B, bg=BTN_BG, fg=FG_TEXT, 
                                         activebackground=BTN_ACTIVE, activeforeground=FG_TEXT, relief=tk.SOLID, bd=1)
        self.btn_comparativo.pack(pady=(0, 15))

        self.btn_localizacao = tk.Button(root, text="BUSCA LOCALIZADA", command=self.abrir_localizacao, 
                                         width=40, height=3, font=FONT_HUD_B, bg=BTN_BG, fg=FG_TEXT, 
                                         activebackground=BTN_ACTIVE, activeforeground=FG_TEXT, relief=tk.SOLID, bd=1)
        self.btn_localizacao.pack(pady=(0, 20))

    # =======================================================
    # ATIVAÇÃO DO SCROLL DO MOUSE
    # =======================================================
    def _ativar_scroll(self, canvas, frame):
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    # =======================================================
    # MOTORES DE INTELIGÊNCIA
    # =======================================================
    def extrair_nomes(self, texto):
        if not texto or str(texto).lower() == 'nan': return []
        nfkd = unicodedata.normalize('NFKD', str(texto))
        limpo = re.sub(r'[^a-zA-Z\s]', '', u"".join([c for c in nfkd if not unicodedata.combining(c)]))
        limpo = " ".join(limpo.split()).upper()
        return [limpo] if len(limpo) > 2 else []

    def is_cpf_valido(self, cpf):
        if len(cpf) != 11 or cpf == cpf[0] * 11: return False
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        d1 = 11 - (soma % 11)
        if int(cpf[9]) != (0 if d1 >= 10 else d1): return False
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        d2 = 11 - (soma % 11)
        if int(cpf[10]) != (0 if d2 >= 10 else d2): return False
        return True

    def extrair_cpfs_validos(self, texto):
        cpfs = set()
        for match in re.finditer(r'(?:\d[^\d]{0,2}){10}\d', str(texto)):
            possivel = re.sub(r'\D', '', match.group(0))
            if len(possivel) == 11 and self.is_cpf_valido(possivel):
                cpfs.add(f"{possivel[:3]}.{possivel[3:6]}.{possivel[6:9]}-{possivel[9:]}")
        return list(cpfs)

    def extrair_telefones(self, texto):
        telefones = set()
        for match in re.finditer(r'(?:\+?55\s?)?\(?0?[1-9]{2}\)?[\s\-]*(?:9[\s\-]?)?\d{4}[\s\-]?\d{4}', str(texto)):
            num = re.sub(r'\D', '', match.group(0)) 
            if num.startswith('55') and len(num) >= 12: num = num[2:]
            if num.startswith('0') and len(num) >= 11: num = num[1:]
            if len(num) in [10, 11]: telefones.add(num)
        return list(telefones)
        
    def extrair_emails(self, texto):
        emails = set()
        for match in re.finditer(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', str(texto)):
            emails.add(match.group(0).lower())
        return list(emails)

    # =======================================================
    # FUNCIONALIDADE 1: COMPARATIVO AVANÇADO
    # =======================================================
    def abrir_comparativo(self):
        self.win_comp = tk.Toplevel(self.root)
        self.win_comp.title("Comparativo de Dados")
        self.win_comp.geometry("950x800")
        self.win_comp.configure(bg=BG_COLOR, padx=15, pady=15)
        self.win_comp.grab_set()
        
        self.arquivos_comp = []
        self.check_vars = []
        self.dicionario_originais = {}
        self.linhas_vistas = set()

        tk.Label(self.win_comp, text="PROCESSAMENTO COMPARATIVO", font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 10))
        
        frame_opcoes = tk.Frame(self.win_comp, bg=PANEL_BG, highlightbackground=FG_COLOR, highlightthickness=1, padx=10, pady=10)
        frame_opcoes.pack(fill=tk.X, pady=5)

        self.var_comp_nome = tk.BooleanVar(value=True)
        self.var_comp_cpf = tk.BooleanVar(value=False)
        self.var_comp_tel = tk.BooleanVar(value=False)
        self.var_comp_email = tk.BooleanVar(value=False)

        tk.Label(frame_opcoes, text="Campos:", font=FONT_HUD_B, bg=PANEL_BG, fg=FG_COLOR).pack(side=tk.LEFT, padx=(0,10))
        
        # --- SOLUÇÃO DO BUG DOS CHECKBOXES SUPERIORES ---
        # A caixinha é separada do texto, garantindo que o V continue preto no fundo branco.
        for text, var in [("Nome", self.var_comp_nome), ("CPF", self.var_comp_cpf), ("Telefone", self.var_comp_tel), ("E-mail", self.var_comp_email)]:
            tk.Checkbutton(frame_opcoes, variable=var, bg=PANEL_BG, selectcolor="#FFFFFF", activebackground=PANEL_BG).pack(side=tk.LEFT, padx=(5, 0))
            tk.Label(frame_opcoes, text=text, font=FONT_HUD, bg=PANEL_BG, fg=FG_TEXT).pack(side=tk.LEFT, padx=(0, 5))

        tk.Label(frame_opcoes, text="| Mín. Fontes:", font=FONT_HUD_B, bg=PANEL_BG, fg=FG_COLOR).pack(side=tk.LEFT, padx=(20,5))
        self.var_limite = tk.IntVar(value=2)
        
        self.spin_limite = tk.Spinbox(frame_opcoes, from_=2, to=2, width=5, state="disabled", font=FONT_HUD_B, 
                                      textvariable=self.var_limite, bg=PANEL_BG, fg=FG_TEXT, 
                                      readonlybackground=PANEL_BG, buttonbackground=BTN_BG)
        self.spin_limite.pack(side=tk.LEFT)

        frame_add = tk.Frame(self.win_comp, bg=BG_COLOR)
        frame_add.pack(pady=10, fill=tk.X)
        self.btn_add_arquivo = tk.Button(frame_add, text="Adicionar Arquivo", command=self.adicionar_arquivo_comp, font=FONT_HUD_B, bg=BTN_BG, fg=FG_TEXT, relief=tk.SOLID, bd=1)
        self.btn_add_arquivo.pack(side=tk.LEFT, padx=2)
        self.btn_rem_arquivo = tk.Button(frame_add, text="Remover", command=self.remover_arquivo_comp, font=FONT_HUD_B, bg=BTN_BG, fg=WARN_COLOR, relief=tk.SOLID, bd=1)
        self.btn_rem_arquivo.pack(side=tk.LEFT, padx=2)
        
        self.listbox_arquivos = tk.Listbox(self.win_comp, height=4, font=FONT_HUD, bg=PANEL_BG, fg=FG_TEXT, selectbackground=BTN_ACTIVE, relief=tk.FLAT, highlightthickness=1, highlightbackground=FG_COLOR)
        self.listbox_arquivos.pack(fill=tk.X, pady=5)

        self.btn_processar_comp = tk.Button(self.win_comp, text="PROCESSAR DADOS", command=self.iniciar_processamento_thread, height=2, font=FONT_TITLE, bg="#0E4A35", fg=OK_COLOR, relief=tk.SOLID, bd=1)
        self.btn_processar_comp.pack(fill=tk.X, pady=10)

        # BLOCO DA BARRA DE PROGRESSO
        self.frame_loading = tk.Frame(self.win_comp, bg=BG_COLOR)
        self.progress_bar = ProgressBarHUD(self.frame_loading, width=500, height=25)
        self.progress_bar.pack(pady=5)

        container_frame = tk.Frame(self.win_comp, bg=PANEL_BG, highlightbackground=FG_COLOR, highlightthickness=1)
        container_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.canvas_comp = tk.Canvas(container_frame, bg=PANEL_BG, highlightthickness=0)
        self.scrollbar_y = ttk.Scrollbar(container_frame, orient="vertical", command=self.canvas_comp.yview)
        self.scrollbar_x = ttk.Scrollbar(container_frame, orient="horizontal", command=self.canvas_comp.xview)
        
        self.scrollable_frame_comp = tk.Frame(self.canvas_comp, bg=PANEL_BG)
        self.scrollable_frame_comp.bind("<Configure>", lambda e: self.canvas_comp.configure(scrollregion=self.canvas_comp.bbox("all")))
        self.canvas_comp.create_window((0, 0), window=self.scrollable_frame_comp, anchor="nw")
        self.canvas_comp.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas_comp.pack(side="left", fill="both", expand=True)
        
        self._ativar_scroll(self.canvas_comp, self.scrollable_frame_comp)
        
        self.btn_exportar_comp = tk.Button(self.win_comp, text="EXPORTAR RELATÓRIO (.ZIP)", command=self.exportar_comparativo, height=2, state=tk.DISABLED, font=FONT_HUD_B, bg=BTN_BG, fg=FG_ALT, relief=tk.SOLID, bd=1)
        self.btn_exportar_comp.pack(fill=tk.X, pady=10)

    def atualizar_limites(self):
        qtd = len(self.arquivos_comp)
        if qtd >= 2:
            self.spin_limite.config(state="normal", from_=2, to=qtd)
            self.var_limite.set(qtd)
            self.spin_limite.config(state="readonly")
        else:
            self.spin_limite.config(state="normal")
            self.var_limite.set(2)
            self.spin_limite.config(state="disabled")

    def atualizar_listbox(self):
        self.listbox_arquivos.delete(0, tk.END)
        for i, arq in enumerate(self.arquivos_comp):
            self.listbox_arquivos.insert(tk.END, f" {i+1}. {os.path.basename(arq)}")

    def adicionar_arquivo_comp(self):
        caminhos = filedialog.askopenfilenames(title="Selecione os arquivos", filetypes=[("Planilhas e Texto", "*.xlsx *.xls *.txt *.csv")], parent=self.win_comp)
        for c in caminhos:
            if c not in self.arquivos_comp:
                self.arquivos_comp.append(c)
        self.atualizar_listbox()
        self.atualizar_limites()

    def remover_arquivo_comp(self):
        selecionados = self.listbox_arquivos.curselection()
        if not selecionados: return
        del self.arquivos_comp[selecionados[0]]
        self.atualizar_listbox()
        self.atualizar_limites()

    def limpar_arquivos_comp(self):
        self.arquivos_comp.clear()
        self.atualizar_listbox()
        self.atualizar_limites()
        for widget in self.scrollable_frame_comp.winfo_children(): widget.destroy()
        self.btn_exportar_comp.config(state=tk.DISABLED, fg=FG_ALT)

    def _seguro_erro(self, msg):
        messagebox.showerror("Erro de Processamento", msg, parent=self.win_comp)
        self.frame_loading.pack_forget()
        self.btn_processar_comp.config(state=tk.NORMAL)

    def iniciar_processamento_thread(self):
        if len(self.arquivos_comp) < 2:
            messagebox.showwarning("Atenção", "Adicione pelo menos 2 arquivos.", parent=self.win_comp); return

        sel = []
        if self.var_comp_nome.get(): sel.append("Nome")
        if self.var_comp_cpf.get(): sel.append("CPF")
        if self.var_comp_tel.get(): sel.append("Telefone")
        if self.var_comp_email.get(): sel.append("E-mail")

        if not sel:
            messagebox.showwarning("Atenção", "Selecione pelo menos um campo.", parent=self.win_comp); return

        for widget in self.scrollable_frame_comp.winfo_children(): widget.destroy()
        self.btn_processar_comp.config(state=tk.DISABLED)
        
        self.frame_loading.pack(fill=tk.X, pady=5, before=self.btn_exportar_comp)
        self.progress_bar.update_progress(0, "Iniciando Preparativos...")
        
        threading.Thread(target=self._processar_comparativo_back, args=(sel,), daemon=True).start()

    def _processar_comparativo_back(self, selecionados):
        minimo_exigido = int(self.spin_limite.get())
        self.check_vars.clear()
        self.dicionario_originais.clear()
        self.linhas_vistas.clear()
        mapa_arquivos_encontrados = {}
        total_arquivos = len(self.arquivos_comp)

        try:
            for idx_arquivo, caminho in enumerate(self.arquivos_comp):
                pct = (idx_arquivo / total_arquivos) * 100
                self.root.after(0, self.progress_bar.update_progress, pct, f"Lendo Arquivo {idx_arquivo+1}/{total_arquivos}")
                
                ext = os.path.splitext(caminho)[1].lower()
                nome_arquivo = os.path.basename(caminho)
                
                if ext == '.txt':
                    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
                        for linha in f:
                            linha_str = str(linha).strip()
                            if not linha_str: continue
                            nomes = self.extrair_nomes(linha_str) if "Nome" in selecionados else []
                            cpfs = self.extrair_cpfs_validos(linha_str) if "CPF" in selecionados else []
                            tels = self.extrair_telefones(linha_str) if "Telefone" in selecionados else []
                            emails = self.extrair_emails(linha_str) if "E-mail" in selecionados else []
                            
                            chaves_linha = self._gerar_chaves(selecionados, nomes, cpfs, tels, emails)
                            linha_comp = f"[{nome_arquivo}] {linha_str}"
                            
                            for chave in chaves_linha:
                                if chave not in mapa_arquivos_encontrados: mapa_arquivos_encontrados[chave] = set()
                                mapa_arquivos_encontrados[chave].add(idx_arquivo)
                                
                                if chave not in self.dicionario_originais: self.dicionario_originais[chave] = []
                                assinatura_linha = f"{chave}|{linha_comp}"
                                if assinatura_linha not in self.linhas_vistas:
                                    self.linhas_vistas.add(assinatura_linha)
                                    self.dicionario_originais[chave].append({'Arquivo': nome_arquivo, 'Aba': 'N/A', 'Dados': linha_comp})

                elif ext in ['.xlsx', '.xls']:
                    xls = pd.ExcelFile(caminho)
                    for aba in xls.sheet_names:
                        df = pd.read_excel(xls, sheet_name=aba)
                        df.dropna(how='all', inplace=True)
                        
                        colunas_nome = [i for i, col in enumerate(df.columns) if any(p in str(col).lower() for p in ['nome', 'titular', 'cliente', 'razao', 'paciente'])]
                        
                        df_str = df.astype(str)
                        for row in df_str.itertuples(index=False, name=None):
                            val_strs = [str(v).strip() for v in row]
                            valid_vals = [(df.columns[i], v) for i, v in enumerate(val_strs) if v and v != 'nan']
                            
                            if not valid_vals: continue
                            
                            linha_completa_texto = " ".join([v for _, v in valid_vals])
                            valores_colunas = [f"{c}: {v}" for c, v in valid_vals]
                            
                            nomes_linha, cpfs_linha, tels_linha, emails_linha = set(), set(), set(), set()
                            
                            if "CPF" in selecionados: cpfs_linha.update(self.extrair_cpfs_validos(linha_completa_texto))
                            if "Telefone" in selecionados: tels_linha.update(self.extrair_telefones(linha_completa_texto))
                            if "E-mail" in selecionados: emails_linha.update(self.extrair_emails(linha_completa_texto))
                            if "Nome" in selecionados:
                                for i in colunas_nome:
                                    v = val_strs[i]
                                    if v and v != 'nan': nomes_linha.update(self.extrair_nomes(v))

                            chaves_linha = self._gerar_chaves(selecionados, list(nomes_linha), list(cpfs_linha), list(tels_linha), list(emails_linha))
                            if not chaves_linha: continue
                            
                            linha_comp = f"[{nome_arquivo} | {aba}] " + " | ".join(valores_colunas)
                            
                            for chave in chaves_linha:
                                if chave not in mapa_arquivos_encontrados: mapa_arquivos_encontrados[chave] = set()
                                mapa_arquivos_encontrados[chave].add(idx_arquivo)
                                
                                if chave not in self.dicionario_originais: self.dicionario_originais[chave] = []
                                assinatura_linha = f"{chave}|{linha_comp}"
                                if assinatura_linha not in self.linhas_vistas:
                                    self.linhas_vistas.add(assinatura_linha)
                                    self.dicionario_originais[chave].append({'Arquivo': nome_arquivo, 'Aba': aba, 'Dados': linha_comp})

            self.root.after(0, self.progress_bar.update_progress, 99, "Organizando Resultados...")
            chaves_validadas = [chave for chave, indices in mapa_arquivos_encontrados.items() if len(indices) >= minimo_exigido]
            
            self.root.after(0, self._renderizar_resultados, chaves_validadas, mapa_arquivos_encontrados)

        except Exception as e:
            self.root.after(0, self._seguro_erro, str(e))

    def _gerar_chaves(self, selecionados, nomes, cpfs, tels, emails):
        chaves = set()
        dados_map = {'Nome': nomes, 'CPF': cpfs, 'Telefone': tels, 'E-mail': emails}
        listas = [dados_map[cat] for cat in selecionados if dados_map[cat]]
        if len(listas) != len(selecionados): return chaves 
        for combinacao in itertools.product(*listas): chaves.add(" | ".join(combinacao))
        return chaves

    def _renderizar_resultados(self, chaves_validadas, mapa_arquivos_encontrados):
        self.frame_loading.pack_forget() 
        self.btn_processar_comp.config(state=tk.NORMAL)

        if not chaves_validadas:
            tk.Label(self.scrollable_frame_comp, text="Nenhum resultado atingiu os critérios.", font=FONT_HUD_B, bg=PANEL_BG, fg=WARN_COLOR).grid(row=0, column=0, pady=10, padx=10)
            self.btn_exportar_comp.config(state=tk.DISABLED, fg=FG_ALT, highlightbackground=BG_COLOR)
            return

        self.btn_exportar_comp.config(state=tk.NORMAL, fg=OK_COLOR, highlightbackground=OK_COLOR)
        
        max_fontes = max(len(mapa_arquivos_encontrados[c]) for c in chaves_validadas)
        total_encontrado = len(chaves_validadas)
        
        tk.Label(self.scrollable_frame_comp, text=f"RESULTADOS ENCONTRADOS: {total_encontrado}", font=FONT_TITLE, bg=PANEL_BG, fg=OK_COLOR).grid(row=0, column=0, columnspan=max_fontes+3, pady=(5, 15), padx=5, sticky="w")
        
        tk.Label(self.scrollable_frame_comp, text="Exp.", font=FONT_HUD_B, bg=PANEL_BG, fg=FG_COLOR).grid(row=1, column=0, padx=5, pady=5)
        tk.Label(self.scrollable_frame_comp, text="Tabelas", font=FONT_HUD_B, bg=PANEL_BG, fg=FG_COLOR).grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.scrollable_frame_comp, text="Chave Identificada", font=FONT_HUD_B, bg=PANEL_BG, fg=FG_COLOR).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        for i in range(max_fontes):
            tk.Label(self.scrollable_frame_comp, text=f"Fonte {i+1}", font=FONT_HUD_B, bg=PANEL_BG, fg=FG_COLOR).grid(row=1, column=3+i, padx=5, pady=5, sticky="w")

        LIMITE_VISUAL = 500
        chaves_ordenadas = sorted(chaves_validadas)
        
        for row_idx, chave in enumerate(chaves_ordenadas[:LIMITE_VISUAL], start=2):
            var = tk.BooleanVar(value=True) 
            self.check_vars.append((var, chave))
            
            indices = sorted(list(mapa_arquivos_encontrados[chave]))
            qtd_presencas = len(indices)
            
            # Checkbox idêntico ao de cima
            tk.Checkbutton(self.scrollable_frame_comp, variable=var, bg=PANEL_BG, selectcolor="#FFFFFF", activebackground=PANEL_BG).grid(row=row_idx, column=0, padx=5, pady=2)
            
            tk.Label(self.scrollable_frame_comp, text=str(qtd_presencas), font=FONT_HUD, bg=PANEL_BG, fg=FG_TEXT).grid(row=row_idx, column=1, padx=5, pady=2)
            tk.Label(self.scrollable_frame_comp, text=chave, font=FONT_HUD, bg=PANEL_BG, fg=FG_TEXT).grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
            
            for col_idx in range(max_fontes):
                fname = os.path.basename(self.arquivos_comp[indices[col_idx]]) if col_idx < qtd_presencas else "-"
                tk.Label(self.scrollable_frame_comp, text=fname, font=FONT_HUD, bg=PANEL_BG, fg=FG_TEXT).grid(row=row_idx, column=3+col_idx, padx=5, pady=2, sticky="w")

        if total_encontrado > LIMITE_VISUAL:
            for chave_oculta in chaves_ordenadas[LIMITE_VISUAL:]:
                var_oculta = tk.BooleanVar(value=True)
                self.check_vars.append((var_oculta, chave_oculta))
            
            msg_ocultos = f"+ {total_encontrado - LIMITE_VISUAL} resultados estão ocultos na tela para não causar travamentos. (Todos serão exportados)"
            tk.Label(self.scrollable_frame_comp, text=msg_ocultos, font=("Segoe UI", 10, "italic"), bg=PANEL_BG, fg=WARN_COLOR).grid(row=LIMITE_VISUAL+2, column=0, columnspan=max_fontes+3, pady=10, sticky="w", padx=10)

    def exportar_comparativo(self):
        chaves_export = [chave for var, chave in self.check_vars if var.get()]
        if not chaves_export: return

        caminho_salvar = filedialog.asksaveasfilename(defaultextension=".zip", initialfile="Relatorio_SearchCRT.zip", filetypes=[("Arquivo Zipado", "*.zip")], parent=self.win_comp)
        if not caminho_salvar: return

        nome_base = os.path.splitext(os.path.basename(caminho_salvar))[0]
        dados_tabela = []
        linhas_txt = []

        for chave in chaves_export:
            linhas_txt.append(f"[{chave}]")
            for o in self.dicionario_originais[chave]:
                dados_tabela.append({"Chave": chave, "Fonte": o['Arquivo'], "Aba": o['Aba'], "Dados": o['Dados']})
                linhas_txt.append(o['Dados'])
            linhas_txt.append("")

        df_export = pd.DataFrame(dados_tabela)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                p_txt, p_csv, p_xlsx = [os.path.join(tmpdir, f"{nome_base}{ext}") for ext in [".txt", ".csv", ".xlsx"]]
                with open(p_txt, 'w', encoding='utf-8') as f: f.write("\n".join(linhas_txt))
                df_export.to_csv(p_csv, index=False, sep=';', encoding='utf-8-sig')
                df_export.to_excel(p_xlsx, index=False)
                with zipfile.ZipFile(caminho_salvar, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for p in [p_txt, p_csv, p_xlsx]: zf.write(p, os.path.basename(p))
            messagebox.showinfo("Sucesso", "Exportação concluída com sucesso!", parent=self.win_comp)
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self.win_comp)

    # =======================================================
    # FUNCIONALIDADE 2: LOCALIZAÇÃO GERAL
    # =======================================================
    def abrir_localizacao(self):
        self.win_loc = tk.Toplevel(self.root)
        self.win_loc.title("Busca Localizada")
        self.win_loc.geometry("600x600")
        self.win_loc.configure(bg=BG_COLOR, padx=20, pady=20)
        self.win_loc.grab_set() 
        self.resultados_loc = []

        tk.Label(self.win_loc, text="RASTREIO ESPECÍFICO", font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 10))

        frame_loc = tk.Frame(self.win_loc, bg=PANEL_BG, highlightbackground=FG_COLOR, highlightthickness=1, padx=10, pady=10)
        frame_loc.pack(fill=tk.X, pady=5)
        
        tk.Label(frame_loc, text="Tipo de Dado:", font=FONT_HUD_B, bg=PANEL_BG, fg=FG_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        # Correção visual no Combobox
        style = ttk.Style()
        style.configure("TCombobox", fieldbackground="#FFFFFF", background="#FFFFFF", foreground="#000000")
        
        self.combo_loc = ttk.Combobox(frame_loc, values=["Nome", "CPF", "Telefone", "E-mail", "Município"], state="readonly", width=20, font=FONT_HUD)
        self.combo_loc.current(4)
        self.combo_loc.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame_loc, text="Termo Alvo:", font=FONT_HUD_B, bg=PANEL_BG, fg=FG_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_busca = tk.Entry(frame_loc, width=35, font=FONT_HUD, bg="#FFFFFF", fg="#000000", insertbackground="#000000", bd=1)
        self.entry_busca.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.btn_buscar_loc = tk.Button(self.win_loc, text="SELECIONAR FONTE E BUSCAR", command=self.iniciar_busca_thread, height=2, font=FONT_HUD_B, bg="#0E4A35", fg=OK_COLOR, relief=tk.SOLID, bd=1)
        self.btn_buscar_loc.pack(fill=tk.X, pady=15)
        
        self.frame_loading_loc = tk.Frame(self.win_loc, bg=BG_COLOR)
        self.progress_bar_loc = ProgressBarHUD(self.frame_loading_loc, width=500, height=25)
        self.progress_bar_loc.pack(pady=5)
        
        self.txt_relatorio_loc = tk.Text(self.win_loc, height=12, state=tk.DISABLED, font=FONT_HUD, bg=PANEL_BG, fg=FG_TEXT, bd=1, relief=tk.SOLID, highlightbackground=FG_COLOR)
        self.txt_relatorio_loc.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.btn_exportar_loc = tk.Button(self.win_loc, text="EXPORTAR RESULTADOS", command=self.exportar_localizacao, height=2, state=tk.DISABLED, font=FONT_HUD_B, bg=BTN_BG, fg=FG_ALT, relief=tk.SOLID, bd=1)
        self.btn_exportar_loc.pack(fill=tk.X)

    def iniciar_busca_thread(self):
        termo = self.entry_busca.get().strip()
        cat = self.combo_loc.get()
        
        if cat == "CPF" and not self.extrair_cpfs_validos(termo): messagebox.showwarning("Erro", "CPF Inválido.", parent=self.win_loc); return
        elif cat == "Telefone" and not self.extrair_telefones(termo): messagebox.showwarning("Erro", "Telefone Inválido.", parent=self.win_loc); return
        elif cat == "E-mail" and not self.extrair_emails(termo): messagebox.showwarning("Erro", "E-mail Inválido.", parent=self.win_loc); return
        elif cat in ["Nome", "Município"] and not self.extrair_nomes(termo): messagebox.showwarning("Erro", "Termo Inválido.", parent=self.win_loc); return
            
        caminho_arquivo = filedialog.askopenfilename(title="Selecione a planilha", filetypes=[("Planilhas", "*.xlsx *.xls *.odf *.ods")], parent=self.win_loc)
        if not caminho_arquivo: return
        
        self.txt_relatorio_loc.config(state=tk.NORMAL)
        self.txt_relatorio_loc.delete("1.0", tk.END)
        self.txt_relatorio_loc.config(state=tk.DISABLED)
        self.btn_buscar_loc.config(state=tk.DISABLED)
        
        self.frame_loading_loc.pack(fill=tk.X, pady=5, before=self.txt_relatorio_loc)
        self.progress_bar_loc.update_progress(0, "Iniciando Preparativos...")
        
        threading.Thread(target=self._buscar_localizacao_back, args=(caminho_arquivo, cat, termo), daemon=True).start()

    def _buscar_localizacao_back(self, caminho_arquivo, categoria, termo_digitado):
        termo_busca = ""
        if categoria == "CPF": termo_busca = self.extrair_cpfs_validos(termo_digitado)[0]
        elif categoria == "Telefone": termo_busca = self.extrair_telefones(termo_digitado)[0]
        elif categoria == "E-mail": termo_busca = self.extrair_emails(termo_digitado)[0]
        else: termo_busca = self.extrair_nomes(termo_digitado)[0]

        linhas_encontradas = set()
        try:
            self.root.after(0, self.progress_bar_loc.update_progress, 10, "Lendo Arquivo...")
            xls = pd.ExcelFile(caminho_arquivo)
            total_abas = len(xls.sheet_names)
            
            for i, aba in enumerate(xls.sheet_names):
                self.root.after(0, self.progress_bar_loc.update_progress, ((i+1)/total_abas)*90, f"Varrendo Aba {i+1}/{total_abas}")
                df = pd.read_excel(xls, sheet_name=aba)
                df.dropna(how='all', inplace=True)
                df_str = df.astype(str)
                
                for row in df_str.itertuples(index=False, name=None):
                    match_encontrado = False
                    for val in row:
                        val_str = str(val).strip() 
                        if val_str == 'nan': continue
                        if categoria == "Município" and termo_busca in self.extrair_nomes(val_str): match_encontrado = True; break
                        elif categoria == "Nome" and termo_busca in self.extrair_nomes(val_str): match_encontrado = True; break
                        elif categoria == "CPF" and termo_busca in self.extrair_cpfs_validos(val_str): match_encontrado = True; break
                        elif categoria == "Telefone" and termo_busca in self.extrair_telefones(val_str): match_encontrado = True; break
                        elif categoria == "E-mail" and termo_busca in self.extrair_emails(val_str): match_encontrado = True; break
                    
                    if match_encontrado:
                        valores_linha = [f"{df.columns[idx]}: {v}" for idx, v in enumerate(row) if str(v).strip() != 'nan']
                        linhas_encontradas.add(f"[{aba}] " + " | ".join(valores_linha))
            
            self.root.after(0, self._renderizar_busca, termo_busca, list(linhas_encontradas))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", str(e), parent=self.win_loc))
            self.root.after(0, self.frame_loading_loc.pack_forget)
            self.root.after(0, lambda: self.btn_buscar_loc.config(state=tk.NORMAL))

    def _renderizar_busca(self, termo_busca, linhas_encontradas):
        self.frame_loading_loc.pack_forget()
        self.btn_buscar_loc.config(state=tk.NORMAL)
        
        self.resultados_loc = sorted(linhas_encontradas)
        self.txt_relatorio_loc.config(state=tk.NORMAL)
        
        if self.resultados_loc:
            resumo = f"DADOS LOCALIZADOS: {len(self.resultados_loc)}\n" + "-"*40 + "\n"
            for linea in self.resultados_loc[:5]: resumo += f"> {linea}\n"
            if len(self.resultados_loc) > 5: resumo += f"... [+{len(self.resultados_loc)-5} OCULTOS]\n"
            self.txt_relatorio_loc.insert(tk.END, resumo)
            self.btn_exportar_loc.config(state=tk.NORMAL, fg=OK_COLOR)
        else:
            self.txt_relatorio_loc.insert(tk.END, f"Nenhum resultado encontrado para: {termo_busca}")
            self.btn_exportar_loc.config(state=tk.DISABLED, fg=FG_ALT)
            
        self.txt_relatorio_loc.config(state=tk.DISABLED)

    def exportar_localizacao(self):
        caminho_salvar = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="SearchCRT_Busca.txt", filetypes=[("Texto", "*.txt")], parent=self.win_loc)
        if not caminho_salvar: return
        try:
            with open(caminho_salvar, 'w', encoding='utf-8') as f:
                for registro in self.resultados_loc: f.write(registro + '\n')
            messagebox.showinfo("Sucesso", "Exportação concluída.", parent=self.win_loc)
        except Exception as e:
            messagebox.showerror("Erro", str(e), parent=self.win_loc)

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchCRTApp(root)
    root.mainloop()