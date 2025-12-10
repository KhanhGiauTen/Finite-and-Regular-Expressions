import os
import tkinter as tk
from tkinter import ttk, messagebox

import graphviz
from PIL import Image, ImageTk

from automata import RegexToNFAConverter, nfa_to_dfa


class MiniJFLAP:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini-JFLAP 2.0 (Integrated Regex Engine)")
        self.root.geometry("1100x750")
        self.regex_converter = RegexToNFAConverter()
        
        # Dữ liệu DFA hiện tại
        self.current_dfa = {
            'transitions': {},
            'start': '',
            'final': set()
        }

        # --- TẠO TABS ---
        self.tab_control = ttk.Notebook(root)
        self.tab_regex = ttk.Frame(self.tab_control)
        self.tab_manual = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_regex, text='Nhập Regex')
        self.tab_control.add(self.tab_manual, text='Nhập DFA Thủ công')
        self.tab_control.pack(expand=1, fill="both")

        # --- SETUP UI TỪNG TAB ---
        self.setup_regex_tab()
        self.setup_manual_tab()
        
        # --- KHUNG HIỂN THỊ CHUNG (Bên phải hoặc Dưới) ---
        self.bottom_frame = tk.Frame(root, height=300, bg="#f0f0f0")
        self.bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chia cột: Trái (Ảnh), Phải (Kiểm thử)
        self.viz_frame = tk.LabelFrame(self.bottom_frame, text="Sơ đồ Automata", width=700)
        self.viz_frame.pack(side=tk.LEFT, fill="both", expand=True)
        
        self.test_frame = tk.LabelFrame(self.bottom_frame, text="Chạy Kiểm Thử (Simulator)", width=300)
        self.test_frame.pack(side=tk.RIGHT, fill="y", padx=5)

        # Image Container
        self.img_label = tk.Label(self.viz_frame, text="Chưa có dữ liệu", bg="white")
        self.img_label.pack(fill="both", expand=True)

        # Test Controls
        tk.Label(self.test_frame, text="Nhập chuỗi input:").pack(pady=5)
        self.entry_test = tk.Entry(self.test_frame)
        self.entry_test.pack(fill="x", padx=5)
        
        btn_run = tk.Button(self.test_frame, text="▶ Chạy Mô Phỏng", bg="#2196F3", fg="white", command=self.run_simulation)
        btn_run.pack(fill="x", padx=5, pady=10)
        
        self.log_text = tk.Text(self.test_frame, height=15, width=30, state='disabled')
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def setup_regex_tab(self):
        frame = tk.Frame(self.tab_regex, padx=20, pady=20)
        frame.pack(fill="both")
        
        tk.Label(frame, text="Nhập biểu thức chính quy (Regex):", font=("Arial", 12, "bold")).pack(anchor="w")
        tk.Label(frame, text="Hỗ trợ: ( ) * + (cho union) . (tự động nối)").pack(anchor="w", pady=(0,10))
        
        self.entry_regex = tk.Entry(frame, font=("Arial", 14))
        self.entry_regex.insert(0, "(a+b)*aa(a+b)*")
        self.entry_regex.pack(fill="x", pady=5)
        
        btn_convert = tk.Button(frame, text="Chuyển đổi: Regex -> NFA -> DFA", bg="#4CAF50", fg="white", font=("Arial", 10), command=self.process_regex)
        btn_convert.pack(pady=10)

    def setup_manual_tab(self):
        frame = tk.Frame(self.tab_manual, padx=20, pady=20)
        frame.pack(fill="both")
        
        tk.Label(frame, text="Start State (VD: q0):").grid(row=0, column=0, sticky="w")
        self.man_start = tk.Entry(frame)
        self.man_start.grid(row=0, column=1, sticky="ew")
        
        tk.Label(frame, text="Final States (VD: q1,q2):").grid(row=1, column=0, sticky="w")
        self.man_final = tk.Entry(frame)
        self.man_final.grid(row=1, column=1, sticky="ew")
        
        tk.Label(frame, text="Transitions (q0,a,q1):").grid(row=2, column=0, sticky="nw")
        self.man_trans = tk.Text(frame, height=8, width=40)
        self.man_trans.grid(row=2, column=1)
        
        btn_draw = tk.Button(frame, text="Vẽ & Lưu DFA", command=self.process_manual)
        btn_draw.grid(row=3, column=1, pady=10)

    # --- LOGIC XỬ LÝ ---

    def process_regex(self):
        regex = self.entry_regex.get().strip()
        if not regex: return
        
        try:
            self.log("Đang xử lý Regex: " + regex)
            # 1. Regex -> NFA
            nfa = self.regex_converter.regex_to_nfa(regex)
            # 2. NFA -> DFA
            dfa_raw = nfa_to_dfa(nfa)
            
            # Lưu vào biến global
            self.current_dfa = dfa_raw
            self.current_dfa['start'] = dfa_raw['start'] # Đảm bảo đúng key
            
            self.draw_dfa()
            self.log(f"Thành công! DFA có {len(dfa_raw['transitions'])} trạng thái.")
            messagebox.showinfo("Thành công", "Đã chuyển đổi Regex sang DFA!")
            
        except Exception as e:
            messagebox.showerror("Lỗi Logic", str(e))
            self.log("Lỗi: " + str(e))

    def process_manual(self):
            try:
                start = self.man_start.get().strip()
                # Xử lý Final states
                finals_input = self.man_final.get().split(',')
                finals = {x.strip() for x in finals_input if x.strip()}
                
                trans_text = self.man_trans.get("1.0", tk.END).strip().split('\n')
                
                transitions = {}
                states = set()   # Cần tập hợp này để vẽ node
                alphabet = set() # Cần tập hợp này (tùy chọn)

                # Thêm start và final vào danh sách states trước để đảm bảo không bị thiếu
                if start: states.add(start)
                states.update(finals)

                for line in trans_text:
                    if not line.strip(): continue
                    parts = line.split(',')
                    if len(parts) != 3: continue
                    
                    s, a, d = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    
                    # Thu thập các trạng thái và alphabet
                    states.add(s)
                    states.add(d)
                    alphabet.add(a)

                    if s not in transitions: transitions[s] = {}
                    
                    # --- SỬA ĐỔI QUAN TRỌNG: Dùng List thay vì String ---
                    if a not in transitions[s]: 
                        transitions[s][a] = [] # Khởi tạo list nếu chưa có
                    
                    # Chỉ thêm nếu chưa tồn tại (tránh trùng lặp)
                    if d not in transitions[s][a]:
                        transitions[s][a].append(d)
                    # ----------------------------------------------------
                
                # Cập nhật cấu trúc dữ liệu đầy đủ
                self.current_dfa = {
                    'states': sorted(list(states)), # Bắt buộc phải có key này cho hàm vẽ
                    'alphabet': sorted(list(alphabet)),
                    'transitions': transitions,
                    'start': start,
                    'final': finals
                }
                
                self.draw_dfa()
                self.log("Đã cập nhật DFA/NFA thủ công (Hỗ trợ đa luồng).")
                
            except Exception as e:
                messagebox.showerror("Lỗi nhập liệu", str(e))
                print(e)

    def run_simulation(self):
        start_state = self.current_dfa.get('start')
        transitions = self.current_dfa.get('transitions', {})
        if not start_state or not transitions:
            messagebox.showwarning("Thiếu DFA", "Vui lòng nhập Regex hoặc DFA thủ công trước khi mô phỏng.")
            return

        input_str = self.entry_test.get()
        finals_raw = self.current_dfa.get('final', set())
        final_states = set(finals_raw) if not isinstance(finals_raw, set) else finals_raw

        def format_states(states):
            return '{' + ', '.join(sorted(states)) + '}' if states else '{}'

        current_states = {start_state}
        self.log("=== BẮT ĐẦU MÔ PHỎNG ===")
        self.log(f"Input: '{input_str}'")
        self.log(f"Trạng thái ban đầu: {format_states(current_states)}")

        rejected = False
        for idx, symbol in enumerate(input_str, start=1):
            next_states = set()
            for state in current_states:
                mapping = transitions.get(state, {})
                dest = mapping.get(symbol)
                if dest is None:
                    continue
                if isinstance(dest, list):
                    next_states.update(dest)
                else:
                    next_states.add(dest)

            self.log(f"Bước {idx}: δ{format_states(current_states)} --{symbol}--> {format_states(next_states)}")
            if not next_states:
                rejected = True
                break
            current_states = next_states

        if not input_str:
            self.log("Không có ký tự nào, giữ nguyên trạng thái ban đầu.")

        is_accept = bool(current_states and final_states and current_states.intersection(final_states) and not rejected)
        if is_accept:
            self.log("Kết quả: ACCEPT")
            messagebox.showinfo("Kết quả", "Chuỗi được chấp nhận bởi DFA.")
        else:
            self.log("Kết quả: REJECT")
            messagebox.showwarning("Kết quả", "Chuỗi bị từ chối.")

    def draw_dfa(self):
        if not self.current_dfa: return

        try:
            dot = graphviz.Digraph(format='png')
            dot.attr(rankdir='LR') # Vẽ ngang
            
            # Kiểm tra xem có key 'states' không (đề phòng lỗi logic cũ)
            state_list = self.current_dfa.get('states', [])
            # Nếu list rỗng, thử trích xuất từ transitions
            if not state_list:
                state_list = list(self.current_dfa.get('transitions', {}).keys())

            # 1. Vẽ các nút (States)
            for s in state_list:
                # Nếu s là final state thì vẽ 2 vòng tròn
                shape = 'doublecircle' if s in self.current_dfa.get('final', set()) else 'circle'
                dot.node(str(s), shape=shape)
            
            # 2. Vẽ nút Start ảo
            dot.node('start_hidden', shape='point', width='0')
            start_node = self.current_dfa.get('start', '')
            if start_node and start_node in state_list:
                dot.edge('start_hidden', start_node)

            # 3. Vẽ các cạnh (Transitions) - Hỗ trợ cả NFA (List) và DFA (String)
            trans = self.current_dfa.get('transitions', {})
            for src, mapping in trans.items():
                for char, dest_data in mapping.items():
                    # Nếu đích đến là List (NFA: q0 -> [q1, q0])
                    if isinstance(dest_data, list):
                        for dst in dest_data:
                            dot.edge(str(src), str(dst), label=str(char))
                    # Nếu đích đến là String (DFA cũ: q0 -> q1)
                    else:
                        dot.edge(str(src), str(dest_data), label=str(char))

            # Render
            output_path = "dfa_graph"
            dot.render(output_path, cleanup=True)
            
            # Load ảnh lên GUI
            if os.path.exists(output_path + ".png"):
                img = Image.open(output_path + ".png")
                img.thumbnail((650, 450)) # Resize cho vừa khung
                photo = ImageTk.PhotoImage(img)
                self.img_label.config(image=photo, text="")
                self.img_label.image = photo
            else:
                self.img_label.config(text="Lỗi: Không tìm thấy file ảnh đầu ra.")
                
        except Exception as e:
            self.log("Lỗi vẽ hình (Cài Graphviz chưa?): " + str(e))
            print("Chi tiết lỗi vẽ:", e)

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
