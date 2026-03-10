"""
Saeko CSV Export App
Aplicación Tkinter para exportar datos de estudiantes a CSV
usando la API de Saeko con filtros de School, Term, Program y Group.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import threading
import requests
from auth import SERVICE_ACCOUNT, USER_EMAIL, get_access_token

BASE_URL = "https://app.saeko.io/api/v1"


# ============================================================
# CAPA DE API
# ============================================================

def api_get(endpoint: str, access_token: str, params: dict = None) -> dict:
    """Realiza un GET autenticado a la API de Saeko."""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def get_schools(access_token: str) -> list:
    """GET /core/schools?include_fields=cct"""
    data = api_get("/core/schools", access_token, {"include_fields": "cct"})
    return data.get("schools", [])


def get_terms_by_school(access_token: str, school_id: int) -> list:
    """GET /core/schools/:school_id/terms"""
    data = api_get(f"/core/schools/{school_id}/terms", access_token)
    return data.get("terms", [])


def get_programs_by_school(access_token: str, school_id: int) -> list:
    """GET /core/schools/:school_id/programs?include_fields=internal_code,school_ids"""
    data = api_get(f"/core/schools/{school_id}/programs", access_token,
                   {"include_fields": "internal_code,school_ids"})
    return data.get("programs", [])


def get_groups_by_term(access_token: str, term_id: int) -> list:
    """GET /core/terms/:term_id/groups"""
    data = api_get(f"/core/terms/{term_id}/groups", access_token)
    return data.get("groups", [])


def get_enrollments_by_school(access_token: str, school_id: int,
                              include_fields: str = None, filters: str = None,
                              limit: int = 500, offset: int = 0) -> dict:
    """GET /core/schools/:school_id/enrollments con paginación."""
    params = {"limit": limit, "offset": offset}
    if include_fields:
        params["include_fields"] = include_fields
    if filters:
        params["filters"] = filters
    return api_get(f"/core/schools/{school_id}/enrollments", access_token, params)


def get_all_enrollments(access_token: str, school_id: int,
                        term_id: int = None, program_id: int = None,
                        group_id: int = None, on_progress=None) -> list:
    """
    Obtiene TODOS los enrollments con paginación automática.
    Filtra por term_id, program_id, group_id si se proporcionan.
    """
    include = "student,program_name,group_name,school_name,group_shift"
    filters_parts = []
    if term_id:
        filters_parts.append(f"term_id={term_id}")
    if program_id:
        filters_parts.append(f"program_id={program_id}")
    if group_id:
        filters_parts.append(f"group_id={group_id}")
    filters_str = ";".join(filters_parts) if filters_parts else None

    all_enrollments = []
    offset = 0
    limit = 500
    while True:
        data = get_enrollments_by_school(
            access_token, school_id,
            include_fields=include,
            filters=filters_str,
            limit=limit, offset=offset
        )
        enrollments = data.get("enrollments", [])
        all_enrollments.extend(enrollments)
        total = data.get("meta", {}).get("total", len(all_enrollments))
        if on_progress:
            on_progress(len(all_enrollments), total)
        if len(enrollments) < limit:
            break
        offset += limit
    return all_enrollments


def get_student_detail(access_token: str, student_id: int) -> dict:
    """GET /core/students/:student_id"""
    data = api_get(f"/core/students/{student_id}", access_token)
    return data.get("student", data)


# ============================================================
# APLICACIÓN TKINTER
# ============================================================

class SaekoCSVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Saeko - Exportar CSV Estudiantes")
        self.root.geometry("750x620")
        self.root.resizable(False, False)

        self.access_token = None
        self.schools = []
        self.terms = []
        self.programs = []
        self.groups = []
        self.programs_map = {}  # program_id → program dict

        self._build_ui()
        self._authenticate()

    def _build_ui(self):
        # Frame principal
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(main, text="Exportar Estudiantes a CSV",
                  font=("Segoe UI", 16, "bold")).pack(pady=(0, 15))

        # --- Filtros ---
        filters_frame = ttk.LabelFrame(main, text="Filtros", padding=10)
        filters_frame.pack(fill=tk.X, pady=(0, 10))

        # School
        row0 = ttk.Frame(filters_frame)
        row0.pack(fill=tk.X, pady=3)
        ttk.Label(row0, text="Plantel (School):", width=20, anchor="w").pack(side=tk.LEFT)
        self.school_var = tk.StringVar()
        self.school_combo = ttk.Combobox(row0, textvariable=self.school_var,
                                         state="readonly", width=55)
        self.school_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.school_combo.bind("<<ComboboxSelected>>", self._on_school_selected)

        # Term
        row1 = ttk.Frame(filters_frame)
        row1.pack(fill=tk.X, pady=3)
        ttk.Label(row1, text="Periodo (Term):", width=20, anchor="w").pack(side=tk.LEFT)
        self.term_var = tk.StringVar()
        self.term_combo = ttk.Combobox(row1, textvariable=self.term_var,
                                       state="readonly", width=55)
        self.term_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.term_combo.bind("<<ComboboxSelected>>", self._on_term_selected)

        # Program
        row2 = ttk.Frame(filters_frame)
        row2.pack(fill=tk.X, pady=3)
        ttk.Label(row2, text="Carrera (Program):", width=20, anchor="w").pack(side=tk.LEFT)
        self.program_var = tk.StringVar()
        self.program_combo = ttk.Combobox(row2, textvariable=self.program_var,
                                          state="readonly", width=55)
        self.program_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Group
        row3 = ttk.Frame(filters_frame)
        row3.pack(fill=tk.X, pady=3)
        ttk.Label(row3, text="Grupo (Group):", width=20, anchor="w").pack(side=tk.LEFT)
        self.group_var = tk.StringVar()
        self.group_combo = ttk.Combobox(row3, textvariable=self.group_var,
                                        state="readonly", width=55)
        self.group_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --- Opciones ---
        opts_frame = ttk.LabelFrame(main, text="Opciones", padding=10)
        opts_frame.pack(fill=tk.X, pady=(0, 10))

        self.colegio_var = tk.StringVar(value="Michoacán")
        row_col = ttk.Frame(opts_frame)
        row_col.pack(fill=tk.X, pady=3)
        ttk.Label(row_col, text="Nombre del Colegio:", width=20, anchor="w").pack(side=tk.LEFT)
        ttk.Entry(row_col, textvariable=self.colegio_var, width=57).pack(side=tk.LEFT)

        self.version_var = tk.StringVar(value="V23")
        row_ver = ttk.Frame(opts_frame)
        row_ver.pack(fill=tk.X, pady=3)
        ttk.Label(row_ver, text="Versión Carrera:", width=20, anchor="w").pack(side=tk.LEFT)
        ttk.Entry(row_ver, textvariable=self.version_var, width=57).pack(side=tk.LEFT)

        # --- Botón generar ---
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(5, 10))
        self.btn_generate = ttk.Button(btn_frame, text="Generar CSV",
                                        command=self._on_generate)
        self.btn_generate.pack(side=tk.LEFT, padx=(0, 10))
        self.btn_preview = ttk.Button(btn_frame, text="Vista Previa (10 registros)",
                                       command=self._on_preview)
        self.btn_preview.pack(side=tk.LEFT)

        # --- Barra de progreso ---
        self.progress = ttk.Progressbar(main, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 5))

        self.status_var = tk.StringVar(value="Iniciando...")
        ttk.Label(main, textvariable=self.status_var,
                  font=("Segoe UI", 9)).pack(anchor="w")

        # --- Preview text ---
        self.preview_text = tk.Text(main, height=10, state="disabled",
                                     font=("Consolas", 9))
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    # --- Autenticación ---
    def _authenticate(self):
        self.status_var.set("Autenticando...")
        self._disable_controls()

        def task():
            try:
                token_data = get_access_token(SERVICE_ACCOUNT, USER_EMAIL)
                self.access_token = token_data["access_token"]
                print(self.access_token) # solo para debug, no mostrar completo en producción
                self.root.after(0, self._load_schools)
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda msg=msg: self._show_error("Error de autenticación", msg))

        threading.Thread(target=task, daemon=True).start()

    def _load_schools(self):
        self.status_var.set("Cargando planteles...")

        def task():
            try:
                self.schools = get_schools(self.access_token)
                self.root.after(0, self._populate_schools)
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda msg=msg: self._show_error("Error cargando schools", msg))

        threading.Thread(target=task, daemon=True).start()

    def _populate_schools(self):
        values = []
        for s in self.schools:
            cct = s.get("cct", "")
            name = s.get("name", f"School {s['id']}")
            values.append(f"{s['id']} | {cct} | {name}")
        self.school_combo["values"] = values
        self.status_var.set(f"{len(self.schools)} planteles cargados. Selecciona uno.")
        self._enable_controls()

    # --- Selección en cascada ---
    def _on_school_selected(self, event=None):
        sel = self.school_combo.current()
        if sel < 0:
            return
        school = self.schools[sel]
        school_id = school["id"]
        self.status_var.set(f"Cargando periodos y carreras para {school.get('name', '')}...")
        self._clear_combos("term")
        self._disable_controls()

        def task():
            try:
                self.terms = get_terms_by_school(self.access_token, school_id)
                self.programs = get_programs_by_school(self.access_token, school_id)
                self.programs_map = {p["id"]: p for p in self.programs}
                self.root.after(0, self._populate_terms_programs)
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda msg=msg: self._show_error("Error cargando datos", msg))

        threading.Thread(target=task, daemon=True).start()

    def _populate_terms_programs(self):
        # Terms - ordenar por fecha descendente
        sorted_terms = sorted(self.terms, key=lambda t: t.get("begins_at", ""), reverse=True)
        self.terms = sorted_terms
        term_values = ["-- Todos --"]
        for t in self.terms:
            current = " [ACTUAL]" if t.get("is_current") else ""
            term_values.append(f"{t['id']} | {t['name']} | {t.get('begins_at', '')} → {t.get('ends_at', '')}{current}")
        self.term_combo["values"] = term_values

        # Programs
        prog_values = ["-- Todos --"]
        for p in self.programs:
            code = p.get("internal_code", "")
            prog_values.append(f"{p['id']} | {code} | {p.get('name', '')}")
        self.program_combo["values"] = prog_values

        self.status_var.set(
            f"{len(self.terms)} periodos, {len(self.programs)} carreras. "
            "Selecciona periodo para cargar grupos."
        )
        self._enable_controls()

    def _on_term_selected(self, event=None):
        sel = self.term_combo.current()
        if sel <= 0:  # 0 = "-- Todos --"
            self.group_combo["values"] = ["-- Todos --"]
            self.group_var.set("")
            self.groups = []
            return
        term = self.terms[sel - 1]
        term_id = term["id"]
        self.status_var.set(f"Cargando grupos para {term.get('name', '')}...")

        def task():
            try:
                self.groups = get_groups_by_term(self.access_token, term_id)
                self.root.after(0, self._populate_groups)
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda msg=msg: self._show_error("Error cargando grupos", msg))

        threading.Thread(target=task, daemon=True).start()

    def _populate_groups(self):
        group_values = ["-- Todos --"]
        for g in self.groups:
            group_values.append(f"{g['id']} | {g.get('name', '')}")
        self.group_combo["values"] = group_values
        self.status_var.set(f"{len(self.groups)} grupos cargados.")

    # --- Generación de CSV ---
    def _get_selected_ids(self):
        """Retorna (school_id, term_id, program_id, group_id) o None para 'Todos'."""
        school_sel = self.school_combo.current()
        if school_sel < 0:
            raise ValueError("Selecciona un plantel.")
        school_id = self.schools[school_sel]["id"]

        term_id = None
        term_sel = self.term_combo.current()
        if term_sel > 0:
            term_id = self.terms[term_sel - 1]["id"]

        program_id = None
        prog_sel = self.program_combo.current()
        if prog_sel > 0:
            program_id = self.programs[prog_sel - 1]["id"]

        group_id = None
        group_sel = self.group_combo.current()
        if group_sel > 0:
            group_id = self.groups[group_sel - 1]["id"]

        return school_id, term_id, program_id, group_id

    def _fetch_and_build_rows(self, school_id, term_id, program_id, group_id,
                               on_progress=None, max_rows=None):
        """Obtiene enrollments y construye las filas del CSV."""
        school_sel = self.school_combo.current()
        school = self.schools[school_sel]
        school_name = school.get("name", "")
        school_cct = school.get("cct", "")
        colegio = self.colegio_var.get()
        version = self.version_var.get()

        enrollments = get_all_enrollments(
            self.access_token, school_id,
            term_id=term_id, program_id=program_id, group_id=group_id,
            on_progress=on_progress
        )

        rows = []
        students_fetched = {}
        total = len(enrollments)
        if max_rows:
            enrollments = enrollments[:max_rows]

        for i, enr in enumerate(enrollments):
            if on_progress:
                on_progress(i + 1, total, phase="Procesando estudiantes")

            student_embedded = enr.get("student", {})
            student_id = enr.get("student_id") or student_embedded.get("id")

            # Siempre obtener detalle completo del estudiante (el embebido no trae curp/surnames)
            if student_id and student_id in students_fetched:
                student = students_fetched[student_id]
            elif student_id:
                try:
                    student = get_student_detail(self.access_token, student_id)
                    students_fetched[student_id] = student
                except Exception:
                    student = student_embedded
            else:
                student = student_embedded

            # Obtener datos del programa
            prog_id = enr.get("program_id")
            program = self.programs_map.get(prog_id, {})
            clave_carrera = program.get("internal_code", "")
            nombre_carrera = enr.get("program_name") or program.get("name", "")

            # Turno (shift)
            turno = enr.get("group_shift") or enr.get("shift") or ""

            # Datos del estudiante
            nombre = student.get("first_name") or student.get("name", "")
            surnames = student.get("surnames", [])
            if surnames:
                primer_apellido = surnames[0] if len(surnames) > 0 else ""
                segundo_apellido = surnames[1] if len(surnames) > 1 else ""
            else:
                # Fallback: separar "surname" por espacio
                surname = student.get("surname", "")
                parts = surname.split(" ", 1) if surname else []
                primer_apellido = parts[0] if len(parts) > 0 else ""
                segundo_apellido = parts[1] if len(parts) > 1 else ""
            curp = student.get("curp", "")
            genero = student.get("gender", "")
            email = student.get("email", "")
            matricula = (student.get("student_id") or student.get("student_id_number")
                         or student.get("registration_number") or str(student.get("id", "")))

            rows.append({
                "COLEGIO": colegio,
                "CCT": school_cct,
                "NOMBRE_DE_PLANTEL": school_name,
                "TURNO": turno,
                "VERSION_CARRERA": version,
                "CLAVE_CARRERA": clave_carrera,
                "NOMBRE_CARRERA": nombre_carrera,
                "MATRICULA": matricula,
                "NOMBRE": nombre,
                "PRIMER_APELLIDO": primer_apellido,
                "SEGUNDO_APELLIDO": segundo_apellido,
                "CURP": curp,
                "GENERO": genero,
                "CORREO_ELECTRONICO": email,
            })

        return rows

    def _on_preview(self):
        try:
            school_id, term_id, program_id, group_id = self._get_selected_ids()
        except ValueError as e:
            messagebox.showwarning("Atención", str(e))
            return

        self._disable_controls()
        self.status_var.set("Generando vista previa...")
        self.progress["value"] = 0

        def task():
            try:
                def on_progress(current, total, phase="Descargando enrollments"):
                    pct = (current / max(total, 1)) * 100
                    self.root.after(0, lambda: self.progress.configure(value=pct))
                    self.root.after(0, lambda: self.status_var.set(
                        f"{phase}: {current}/{total}"
                    ))

                rows = self._fetch_and_build_rows(
                    school_id, term_id, program_id, group_id,
                    on_progress=on_progress, max_rows=10
                )
                self.root.after(0, lambda: self._show_preview(rows))
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda msg=msg: self._show_error("Error", msg))
            finally:
                self.root.after(0, self._enable_controls)

        threading.Thread(target=task, daemon=True).start()

    def _show_preview(self, rows):
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", tk.END)
        if not rows:
            self.preview_text.insert(tk.END, "No se encontraron registros con los filtros seleccionados.")
        else:
            headers = list(rows[0].keys())
            self.preview_text.insert(tk.END, " | ".join(headers) + "\n")
            self.preview_text.insert(tk.END, "-" * 120 + "\n")
            for row in rows:
                line = " | ".join(str(row.get(h, ""))[:25] for h in headers)
                self.preview_text.insert(tk.END, line + "\n")
        self.preview_text.configure(state="disabled")
        self.status_var.set(f"Vista previa: {len(rows)} registros mostrados.")
        self.progress["value"] = 100

    def _on_generate(self):
        try:
            school_id, term_id, program_id, group_id = self._get_selected_ids()
        except ValueError as e:
            messagebox.showwarning("Atención", str(e))
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Guardar CSV como...",
            initialfile="estudiantes_saeko.csv"
        )
        if not filepath:
            return

        self._disable_controls()
        self.status_var.set("Generando CSV...")
        self.progress["value"] = 0

        def task():
            try:
                def on_progress(current, total, phase="Descargando enrollments"):
                    pct = (current / max(total, 1)) * 100
                    self.root.after(0, lambda: self.progress.configure(value=pct))
                    self.root.after(0, lambda: self.status_var.set(
                        f"{phase}: {current}/{total}"
                    ))

                rows = self._fetch_and_build_rows(
                    school_id, term_id, program_id, group_id,
                    on_progress=on_progress
                )

                if not rows:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Sin datos", "No se encontraron registros con los filtros seleccionados."
                    ))
                    return

                # Escribir CSV
                headers = [
                    "COLEGIO", "CCT", "NOMBRE_DE_PLANTEL", "TURNO",
                    "VERSION_CARRERA", "CLAVE_CARRERA", "NOMBRE_CARRERA",
                    "MATRICULA", "NOMBRE", "PRIMER_APELLIDO",
                    "SEGUNDO_APELLIDO", "CURP", "GENERO", "CORREO_ELECTRONICO"
                ]
                with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(rows)

                self.root.after(0, lambda: self.status_var.set(
                    f"CSV generado: {len(rows)} registros → {filepath}"
                ))
                self.root.after(0, lambda: self.progress.configure(value=100))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Listo", f"CSV exportado exitosamente.\n{len(rows)} registros guardados en:\n{filepath}"
                ))
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda msg=msg: self._show_error("Error generando CSV", msg))
            finally:
                self.root.after(0, self._enable_controls)

        threading.Thread(target=task, daemon=True).start()

    # --- Helpers UI ---
    def _disable_controls(self):
        for w in (self.school_combo, self.term_combo, self.program_combo,
                  self.group_combo, self.btn_generate, self.btn_preview):
            w.configure(state="disabled")

    def _enable_controls(self):
        for w in (self.school_combo, self.term_combo, self.program_combo,
                  self.group_combo, self.btn_generate, self.btn_preview):
            w.configure(state="readonly" if isinstance(w, ttk.Combobox) else "normal")

    def _clear_combos(self, from_level="term"):
        levels = ["term", "program", "group"]
        combos = [self.term_combo, self.program_combo, self.group_combo]
        data_attrs = ["terms", "programs", "groups"]
        start = levels.index(from_level)
        for i in range(start, len(levels)):
            combos[i]["values"] = []
            combos[i].set("")
            setattr(self, data_attrs[i], [])

    def _show_error(self, title, message):
        self.status_var.set(f"Error: {message[:80]}")
        messagebox.showerror(title, message)
        self._enable_controls()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = SaekoCSVApp(root)
    root.mainloop()
