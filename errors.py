from opcodes import opcodes, opcode_arguments
class SymbolNotDefined(Error):
	def __init__(self,sym):
		Error.__init__(self,str(sym)+" symbol is not defined") 

class MultipleSymbolDefinitions(Error):
	def __init__(self,sym):
		Error.__init__(self,str(sym)+" symbol has been defined more than once")

class MultipleRegisterDefinitions(Error):
	def __init__(self,reg):
		Error.__init__(self,str(reg)+" register has been defined more than once")

class IncorrectNumberofOperands(Error):
	def __init__(self,op,num):
		Error.__init__(self,str(op)+" requires "+str(opcode_arguments[op])+" operands. "+str(num)+" supplied")

class RegisterExceed(Error):
	def __init__(self,num):
		Error.__init__(self,str(num)+" exceeds the number of registers. Maximum number of registers are __")

class NoEnd(Error):
	def __init__(self):
		Error.__init__("Could not find END statement. Put END at the end of the assembly code")

class IllegalLabelName(Error):
	def __init__(self,l):
		Error.__init__(str(l)+" label name is not allowed as it is a valid opcode")

class IllegalOperand(Error):
	def __init__(self,op,actual, expected):
		Error.__init__("You tried using an invalid combination of opcode and operands. Got "+str(actual)+". "str(op)+" requires a "+str(expected)+" argument.")

class IllegalOpcode(Error):
	def __init__(self,op):
		Error.__init__(self,str(op)+" is not a valid opcode")

class IllegalAddress(Error):
	def __init__(self,address):
		Error.__init__(self,str(address)+" does not exist")

class IllegalMacroName(Error):
	def __init__(self,mname):
		Error.__init__(self,"Name of the Macro "+str(mname)+" is already an existing label/Opcode")


#illegal address
#int or float expected
#label name cannot be an opcode name



