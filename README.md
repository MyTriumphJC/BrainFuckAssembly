# BrainFuckAssembly

As the name suggests, this is an assembly-inspired language that compiles to pure brainfuck.

## Here is a list of all the currently supported operations (and their syntax):

### Commands Directly Correlated to Brainfuck
- `INC $$`          Increment address $$
- `DEC $$`          Decrement address $$
- `GET $$`          Get one character from the user and put it in address $$
- `OUT $$`          Output the value at address $$ as an ascii character
- `JIZ $$`          JumpIfZero at address $$
- `RNZ $$`          ReturnNotZero at address $$
- `RAW $$ "BFCode"` Run the raw brainfuck code BFCode at address $$. Assumes that the code also ends at the same address.

### QoL Commands
- `ADD $$ ##`       Add ## to address $$
- `SUB $$ ##`       Subtract ## from address $$
- `CLR $$`          Resets address $$ to 0
- `MOV $$ $$`       Moves the contents of the first address to the second address. The first address is left at 0. If the second address is not empty, it adds the two together.
- `CPY $$ $$ $$`    Like MOV, but uses the third address as a buffer so as to not destroy the first address. Ex, for memory \[A, B, C], CPY $A $B $C would produce \[A+C, B+A, 0]
- `DSP $$ "Msg"`    Uses address $$ as well as the 5 subsequent memory addresses to display the string Msg. Spaces are not allowed in the string; you must use \s in place of all spaces

### Subprocesses*
- `JMP "LblName"`   Jump to label "LblName"
- `LBL "LblName"`   Identifies label "LblName"
- `RTS`             Return To Sender

\*Note that every LBL must have a corresponding RTS, ***BEFORE ANY OTHER LBL***

### Misc.
- `EOP`             End Of Program (Optional, the program does not check for this)
- `NOP`             No-Op command (Does literally nothing)

You may also add line comments with `;`


To compile your .bfa programs, simply run `py compile.py [-h] [-o [LEVEL]] file`
