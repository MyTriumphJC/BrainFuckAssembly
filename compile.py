import sys
import codecs
import argparse
from pathlib import PurePath

COMMAND_PARAM_NUMS = {"ADD": 2,"SUB": 2,"GET": 1,"OUT": 1,"DSP": 2,
                      "CLR": 1,"JIZ": 1,"RNZ": 1,"MOV": 2,"RAW": 2,
                      "CPY": 3,"JMP": 1,"LBL": 1,"INC": 1,"DEC": 1,
                      "RTS": 0,"EOP": 0,"NOP": 0}

def main(path, optimize_level):
   out = f'{PurePath(path).stem}.bf'
   
   with open(path, 'r') as infile:
      code = infile.read()
   
   code = strip(code)       # Returns string commentless and no whitespace
   code = parse(code)       # Returns an array of each command with parameters
   code = preprocess(code)  # Removes JMP and LBL instructions
   code = compile_(code)    # Compiles to BrainFuck
   
   if optimize_level != 0:
      # Removes redundant commands (ex. "><" or "-+")
      code = optimize(code, optimize_level)
   
   with open(out, 'w') as outfile:
      outfile.write(str(code))

def strip(code):
   commentless = ''
   is_comment = False
   for char in code:
      if char == ';':
         is_comment = True
      elif char == '\n':
         is_comment = False
      if not is_comment:
         commentless += char
   
   return "".join(commentless.split())

def parse(code):
   return_list = []
   index = 0
   function = ["MAIN", []]
   while index < len(code):
      command = []
      command.append(code[index:index+3])
      index += 3
      num_params = COMMAND_PARAM_NUMS[command[0]]
      for _ in range(num_params):
         if code[index] in '$#':
            num = ''
            index += 1 # Skips the leading $ or #
            char = code[index]
            while char in '0123456789':
               num += char
               index += 1
               char = code[index]
            command.append(int(num))
         elif code[index] == '"':
            string = ''
            index += 1 # Skips the leading "
            char = code[index]
            while char != '"':
               if char == '\\':
                  index += 1
                  if code[index] == 's':
                     char = ' '
                  else:
                     char = codecs.decode('\\' + code[index], 'unicode_escape')
               string += char
               index += 1
               char = code[index]
            command.append(string)
            index += 1   # To skip the trailing "
      
      
      if command[0] == "LBL":
         function[1].pop() # Doesn't include EOP or RTS
         return_list.append(function)
         function = [command[1], []]
      else:
         function[1].append(command)
   function[1].pop() # Doesn't include EOP or RTS
   return_list.append(function)
   return return_list

def preprocess(code):
   
   main_program = code[0][1]
   labels = code[1:]
   
   did_add_jmp = True
   while did_add_jmp:
      output = []
      did_add_jmp = False
      for command in main_program:
         if command[0] == 'JMP':
            for function in labels:
               if function[0] == command[1]:
                  output += function[1]
                  did_add_jmp = True
                  break
         else:
            output.append(command)
      main_program = output
   
   return main_program

def compile_(code):
   ptr = 0
   bf = ''
   for command in code:
      if command[0] == 'GET':
         bf += move_to(ptr, command[1]) + ','
         ptr = command[1]
      elif command[0] == 'OUT':
         bf += move_to(ptr, command[1]) + '.'
         ptr = command[1]
      elif command[0] == 'JIZ':
         bf += move_to(ptr, command[1]) + '['
         ptr = command[1]
      elif command[0] == 'RNZ':
         bf += move_to(ptr, command[1]) + ']'
         ptr = command[1]
      elif command[0] == "INC":
         bf += move_to(ptr, command[1]) + '+'
         ptr = command[1]
      elif command[0] == "DEC":
         bf += move_to(ptr, command[1]) + '-'
         ptr = command[1]
      elif command[0] == 'ADD':
         bf += move_to(ptr, command[1])
         ptr = command[1]
         bf += '+' * command[2]
      elif command[0] == 'SUB':
         bf += move_to(ptr, command[1])
         ptr = command[1]
         bf += '-' * command[2]
      elif command[0] == 'CLR':
         bf += move_to(ptr, command[1]) + '[-]'
         ptr = command[1]
      elif command[0] == 'DSP':
         bf += move_to(ptr, command[1])
         ptr = command[1]
         bf += print_message_bf(command[2])
      elif command[0] == 'RAW':
         bf += move_to(ptr, command[1])
         ptr = command[1]
         bf += command[2]
      elif command[0] == 'MOV':
         bf += move_to(ptr, command[1])
         ptr = command[1]
         move_1 = move_to(command[1], command[2])
         move_2 = move_to(command[2], command[1])
         bf += '[' + move_1 + '+' + move_2 + '-]'
      elif command[0] == 'CPY':
         bf += move_to(ptr, command[1])
         move_1 = move_to(command[1], command[2])
         move_2 = move_to(command[2], command[3])
         move_3 = move_to(command[3], command[1])
         bf += '[' + move_1 + '+' + move_2 + '+' + move_3 + '-]'
         move_1 = move_to(command[1], command[3])
         bf += move_1 + '[' + move_3 + '+' + move_1 + '-]'
         ptr = command[3]
      elif command[0] != 'NOP':
         raise SyntaxError(f"Unknown command identifier {command[0]}.")
      # bf += '\n'
   return bf

def optimize(code, level):
   for _ in range(level):
      code = opt(code)
   return code

def opt(code):
   final_code = ''
   skip_next = False
   for index, char in enumerate(code):
      if skip_next:
         skip_next = False
         continue
      
      next_ = code[index+1] if index+1 < len(code) else ''
      
      if not is_opposite_commands(char, next_):
         final_code += char
      else:
         skip_next = True
   
   return final_code

def is_opposite_commands(c0, c1):
   return c0 == '<' and c1 == '>' or \
          c0 == '>' and c1 == '<' or \
          c0 == '+' and c1 == '-' or \
          c0 == '-' and c1 == '+'

def print_message_bf(message):
   # Given var 'message' to be printed
   # Uses 6 consecutive memory locations
   # Starts at memory location 0
   # Ends at memory location 0 with each cell cleared
   
   # Initialized the 6 mem loc's to these values:
   # 32 ( )    48 (0)    65 (A)
   # 80 (P)    97 (a)   112 (p)
   
   bf = '++++++++[>++++++>++++++++>++++++++++>++++++++++++>++++++++++++++<<<<<'\
        '-]++++++++++++++++++++++++++++++++>>+>>+'
   locations = [32, 48, 65, 80, 97, 112]
   ptr = 4
   is_escape = False
   for char in message:
      if char == '\\':
         is_escape = True
         continue
      if is_escape:
         char = codecs.decode('\\' + char, 'unicode_escape')
         is_escape = False
      num = ord(char)
      
      # Distance between two ascii vals is at most 127
      best = [128, 0]
      for index, val in enumerate(locations):
         dist = num - val
         if abs(dist) < abs(best[0]):
            best[0] = dist
            best[1] = index
      
      locations[best[1]] += best[0]
      
      move = best[1] - ptr
      if move < 0:
         bf += '<' * -move
      elif move > 0:
         bf += '>' * move
      ptr = best[1]
      
      if best[0] < 0:
         bf += '-' * -best[0]
      elif best[0] > 0:
         bf += '+' * best[0]
      
      bf += '.'
   
   bf += '>' * (5 - ptr)
   bf += '[-]<[-]<[-]<[-]<[-]<[-]'
   
   return bf

def move_to(ptr, new_addr):
   bf = ''
   
   move_to = new_addr - ptr
   if move_to > 0:
      bf += '>' * move_to
   elif move_to < 0:
      bf += '<' * -move_to
   
   return bf


if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('file', help='The destination of the .bfa file')
   parser.add_argument(
      '-o', '--optimize',
      nargs='?',
      const=6,
      default=0,
      metavar='LEVEL',
      help='The number of passes to do when optimizing the compiled BF ' \
           'code. If ommitted, defaults to 0. If no level is provided, ' \
           'defaults to 6.',
   )
   
   names = parser.parse_args()
   
   main(names.file, int(names.optimize))

