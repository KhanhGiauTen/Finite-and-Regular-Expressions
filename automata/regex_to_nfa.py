class RegexToNFAConverter:
    def __init__(self):
        self.state_counter = 0

    def get_new_state(self):
        self.state_counter += 1
        return f"q{self.state_counter}"

    def regex_to_nfa(self, regex):
        # --- 1. Shunting Yard & Thompson (Regex -> NFA) ---
        # --- 1. Shunting Yard & Thompson (Regex -> NFA) ---
        # ---------------------------------------------------------
        # BƯỚC 1: TOKEN HÓA & XỬ LÝ NGỮ CẢNH (Context-Aware Lexer)
        # Mục tiêu: Phân biệt '+' là Input hay Toán tử.
        #           Phân biệt '.' là Input hay phép nối ẩn.
        # ---------------------------------------------------------
        
        # Ký tự dùng nội bộ cho phép nối (Concatenation) để không trùng với dấu chấm '.' của Input
        CONCAT_OP = '&'
        
        tokens = []
        alphabet = set()
        
        # Những ký tự mà nếu đi sau nó là '+', thì '+' đó là TOÁN TỬ (Union)
        # (Tức là: sau ký tự đóng, sau sao, hoặc sau một ký tự thường)
        union_preceders = {')', '*', 'CHAR'}
        
        last_type = None # Lưu loại token trước đó: 'START', 'OP', 'CHAR', 'OPEN'
        
        i = 0
        n = len(regex)
        
        while i < n:
            char = regex[i]
            
            # --- Xử lý ký tự đặc biệt ---
            if char == '(':
                tokens.append('(')
                last_type = 'OPEN'
                
            elif char == ')':
                tokens.append(')')
                last_type = 'CLOSE'
                
            elif char == '*':
                tokens.append('*')
                last_type = 'STAR'
                
            elif char == '+':
                # LOGIC QUAN TRỌNG: Phân biệt + (Sign) và + (Union)
                # Nếu + xuất hiện đầu câu, hoặc sau '(', hoặc sau phép nối -> Là INPUT
                if last_type in ['CLOSE', 'STAR', 'CHAR']:
                    tokens.append('+') # Đây là toán tử Union
                    last_type = 'OP'
                else:
                    tokens.append(('LITERAL', '+')) # Đây là dấu cộng (Input)
                    alphabet.add('+')
                    last_type = 'CHAR'
                    
            elif char == '𝜀' or char == 'E': # Hỗ trợ nhập E thay cho epsilon
                tokens.append(('LITERAL', '')) # Chuỗi rỗng
                alphabet.add('') # (Thực ra epsilon không cần add vào alphabet, nhưng để logic chạy mượt)
                last_type = 'CHAR'
                
            else:
                # Mọi ký tự khác (bao gồm cả dấu chấm ., số 0-9, a-z) đều là INPUT
                tokens.append(('LITERAL', char))
                alphabet.add(char)
                last_type = 'CHAR'
            
            i += 1

        # ---------------------------------------------------------
        # BƯỚC 2: CHÈN PHÉP NỐI ẨN (Implicit Concatenation)
        # Chèn '&' vào giữa: (Char)(Char), (Char)(Open), (Close)(Char), (Star)(Char)...
        # ---------------------------------------------------------
        processed_tokens = []
        for j in range(len(tokens)):
            token = tokens[j]
            processed_tokens.append(token)
            
            if j + 1 < len(tokens):
                next_token = tokens[j+1]
                
                # Kiểm tra xem token hiện tại có phải là kết thúc của một toán hạng không
                is_curr_operand = (token == ')' or token == '*' or isinstance(token, tuple))
                
                # Kiểm tra xem token tiếp theo có phải là bắt đầu của một toán hạng không
                is_next_operand = (next_token == '(' or isinstance(next_token, tuple))
                
                if is_curr_operand and is_next_operand:
                    processed_tokens.append(CONCAT_OP) # Chèn phép nối

        # ---------------------------------------------------------
        # BƯỚC 3: SHUNTING YARD (Infix -> Postfix)
        # ---------------------------------------------------------
        postfix = []
        stack = []
        # Độ ưu tiên: * > & (nối) > + (hợp)
        priority = {'*': 3, CONCAT_OP: 2, '+': 1, '(': 0}
        
        for t in processed_tokens:
            if isinstance(t, tuple): # Là ký tự input (LITERAL)
                postfix.append(t)
            elif t == '(':
                stack.append(t)
            elif t == ')':
                while stack and stack[-1] != '(':
                    postfix.append(stack.pop())
                if stack: stack.pop() # Pop '('
            elif t in priority: # Là toán tử (*, &, +)
                while stack and priority.get(stack[-1], 0) >= priority[t]:
                    postfix.append(stack.pop())
                stack.append(t)
        
        while stack:
            postfix.append(stack.pop())

        # ---------------------------------------------------------
        # BƯỚC 4: THOMPSON'S CONSTRUCTION (Postfix -> NFA)
        # ---------------------------------------------------------
        nfa_stack = []
        self.state_counter = -1
        
        for token in postfix:
            # 4.1. Xử lý Input (LITERAL)
            if isinstance(token, tuple):
                char = token[1] # Lấy ký tự thực tế
                start = self.get_new_state()
                end = self.get_new_state()
                # Nếu char là rỗng (epsilon), transition là key rỗng
                trans = {start: {char: [end]}} if char != '' else {start: {'': [end]}}
                nfa_stack.append((start, end, trans))
                
            # 4.2. Xử lý Phép Nối (Concatenation)
            elif token == CONCAT_OP:
                if len(nfa_stack) < 2: continue # Phòng lỗi
                n2 = nfa_stack.pop()
                n1 = nfa_stack.pop()
                
                # Hợp nhất transitions
                merged_trans = {**n1[2], **n2[2]}
                
                # Nối end n1 -> start n2 bằng epsilon
                if n1[1] not in merged_trans: merged_trans[n1[1]] = {}
                if '' not in merged_trans[n1[1]]: merged_trans[n1[1]][''] = []
                merged_trans[n1[1]][''].append(n2[0])
                
                nfa_stack.append((n1[0], n2[1], merged_trans))
                
            # 4.3. Xử lý Phép Hợp (Union +)
            elif token == '+':
                if len(nfa_stack) < 2: continue
                n2 = nfa_stack.pop()
                n1 = nfa_stack.pop()
                
                start = self.get_new_state()
                end = self.get_new_state()
                trans = {**n1[2], **n2[2]}
                
                # Start -> start n1, start n2 (epsilon)
                trans[start] = {'': [n1[0], n2[0]]}
                
                # End n1, End n2 -> End (epsilon)
                for old_end in [n1[1], n2[1]]:
                    if old_end not in trans: trans[old_end] = {}
                    if '' not in trans[old_end]: trans[old_end][''] = []
                    trans[old_end][''].append(end)
                    
                nfa_stack.append((start, end, trans))
                
            # 4.4. Xử lý Kleene Star (*)
            elif token == '*':
                if not nfa_stack: continue
                n = nfa_stack.pop()
                start = self.get_new_state()
                end = self.get_new_state()
                trans = n[2]
                
                # Start -> Old start OR End (Match 0 or 1)
                trans[start] = {'': [n[0], end]}
                
                # Old end -> Old start (Repeat) OR End (Finish)
                if n[1] not in trans: trans[n[1]] = {}
                if '' not in trans[n[1]]: trans[n[1]][''] = []
                trans[n[1]][''].extend([n[0], end])
                
                nfa_stack.append((start, end, trans))

        if not nfa_stack:
            raise Exception("Biểu thức chính quy không hợp lệ hoặc rỗng!")

        final_nfa = nfa_stack.pop()
        
        # Lọc lại alphabet (loại bỏ chuỗi rỗng nếu có)
        clean_alphabet = sorted([x for x in alphabet if x != ''])
        
        return {
            'states': list(final_nfa[2].keys()) + [final_nfa[1]], 
            'alphabet': clean_alphabet,
            'transitions': final_nfa[2],
            'start': final_nfa[0],
            'final': {final_nfa[1]}
        }
        # Shunting Yard (Infix to Postfix)
        postfix = ""
        stack = []
        priority = {'*': 3, '.': 2, '+': 1, '(': 0}
        
        for c in processed:
            if c not in priority and c != ')':
                postfix += c
            elif c == '(':
                stack.append(c)
            elif c == ')':
                while stack and stack[-1] != '(':
                    postfix += stack.pop()
                stack.pop() # Pop '('
            else:
                while stack and priority.get(stack[-1], 0) >= priority[c]:
                    postfix += stack.pop()
                stack.append(c)
        while stack: postfix += stack.pop()

        # Thompson Construction (Postfix -> NFA)
        nfa_stack = [] # Stack chứa các tuple (start, end, transitions_dict)
        self.state_counter = -1 # Reset counter
        
        for char in postfix:
            if char == '.':
                n2 = nfa_stack.pop()
                n1 = nfa_stack.pop()
                # Nối end của n1 với start của n2 bằng epsilon ('')
                merged_trans = {**n1[2], **n2[2]}
                if n1[1] not in merged_trans: merged_trans[n1[1]] = {}
                # Epsilon transition
                if '' not in merged_trans[n1[1]]: merged_trans[n1[1]][''] = []
                merged_trans[n1[1]][''].append(n2[0])
                nfa_stack.append((n1[0], n2[1], merged_trans))
                
            elif char == '+': # Union
                n2 = nfa_stack.pop()
                n1 = nfa_stack.pop()
                start = self.get_new_state()
                end = self.get_new_state()
                trans = {**n1[2], **n2[2]}
                trans[start] = {'': [n1[0], n2[0]]}
                
                # Nối end của n1, n2 tới end mới bằng epsilon
                if n1[1] not in trans: trans[n1[1]] = {}
                if '' not in trans[n1[1]]: trans[n1[1]][''] = []
                trans[n1[1]][''].append(end)
                
                if n2[1] not in trans: trans[n2[1]] = {}
                if '' not in trans[n2[1]]: trans[n2[1]][''] = []
                trans[n2[1]][''].append(end)
                
                nfa_stack.append((start, end, trans))
                
            elif char == '*': # Kleene Star
                n = nfa_stack.pop()
                start = self.get_new_state()
                end = self.get_new_state()
                trans = n[2]
                
                trans[start] = {'': [n[0], end]} # Start -> old_start OR Start -> End
                
                if n[1] not in trans: trans[n[1]] = {}
                if '' not in trans[n[1]]: trans[n[1]][''] = []
                trans[n[1]][''].extend([n[0], end]) # Old_end -> Old_start OR Old_end -> End
                
                nfa_stack.append((start, end, trans))
                
            else: # Ký tự thường
                start = self.get_new_state()
                end = self.get_new_state()
                trans = {start: {char: [end]}}
                nfa_stack.append((start, end, trans))

        final_nfa = nfa_stack.pop()
        return {
            'states': list(final_nfa[2].keys()) + [final_nfa[1]], # Approximate list
            'alphabet': sorted(list(alphabet)),
            'transitions': final_nfa[2],
            'start': final_nfa[0],
            'final': {final_nfa[1]}
        }
