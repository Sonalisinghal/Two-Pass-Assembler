from opcodes import opcodes,opcode_arguments

#######################classes required######################
class OpcodeField:
	def __init__(self,opcode,binary,virtual_add,operand1=None,operand2=None,operand3=None):
		self.opcode=opcode
		self.binary=binary
		self.operand1=operand1
		self.operand2=operand2
		self.operand3=operand3
		self.virtualAdd=virtual_add
		self.physicalAdd=None
	def __str__(self):
		l=[self.opcode,self.binary,self.operand1,self.operand2,self.operand3,self.virtualAdd,self.physicalAdd]
		print(str(l))

class LiteralField:
	def __init__(self,literal):
		self.value=literal.replace("'","")
		self.physicalAdd=None
	def __str__(self):
		print(self.literal,self.value,self.physicalAdd)

class LabelField:
	def __init__(self,virtualAdd,code): #code = the function that the label belongs to main or name of macro
		self.virtualAdd=virtualAdd
		self.physicalAdd=None
		self.code=code
	def __str__(self):
		print(self.virtualAdd,self.physicalAdd)

class MacroField:
	def __init__(self,macroparameters):
		self.macroparameters=macroparameters
		self.instructionTable=[]
		self.labels=[]
	def __str__(self):
		print(self.macro,self.opcodeTable)
		for i in opcodeTable:
			print(i)

#######################initialization########################
dataTable=set()
symbolTable = {}
literalTable = {}
opcodeTable = []
macroTable = []
instructionTable=[]

instructions = []
num_ins = 0                      #counter to count number of instructions
foundMacroDefinition=False       #flag to check if a macro is being defined

##########################functions###########################
def removeComments(instruction):
	'''
	Input: Single instruction in assembly language as a string
	Output: Instruction in assembly language as a string, without comments

	Parses the instruction passed as input to remove comments, that is,
	any text written beyond the ';' character.
	'''
	if(instruction.find(";")!=(-1)):
		instruction = instruction[0:instruction.find(";")]
	return(instruction)

bin12 = lambda x : ''.join(reversed([str((x >> i) & 1) for i in range(12)] ) )   #returns 12 bit binary address

def checkMacro(instruction):
	if len(instruction)>=2:
		if("MACRO" in instruction[1]):
			return True
	if("MEND" in instruction or "MEND" in instruction) and len(instruction)==1:
		return False

def addMacro(macro,fields):
	if macro not in macroTable:
		macroTable[macro]=MacroField(fields)
	#else throw double macro definition error

def addOpcode(instruction,otable,address):
	opcode=returnOpcode(instruction)
	if opcode in opcodes:
		parameters=returnParameters(instruction)
		if(len(parameters)==opcode_arguments[opcode]):
			if len(parameters)==0:
				of=OpcodeField(opcode,opcodes[opcode],address)
			elif len(parameters)==1:
				of=OpcodeField(opcode,opcodes[opcode],address,parameters[0])
			elif len(parameters)==3:
				of=OpcodeField(opcode,opcodes[opcode],address,parameters[0],parameters[1],parameters[2])
			otable.append(of)

		#else throw incorrectNumberofoperands error
	#else throw illegal opcodes error

def isValidAddress(address):
	if address in dataTable:
		return True
	#else throw undefined address error

def getLabel(instruction):
	if instruction[0].find(':')!=-1:
		return instruction[0][:-1]
	return False

def addLabel(label, address): #Adds detected label to symbol table
	if label not in symbolTable:
		symbolTable[label]=LabelField(address)
	#else throw double label defn error

def getLiteral(instruction): #Checks if passed instruction contains literals
	for token in instruction:
		if(token[0]=="'" and token[-1]=="'"):
			return(token)
	return False

def addLiteral(literal): #Adds literals to Literal Table
	# literalTable.append({"literal":literal,"value":literal[1:-1],"physical_add":None})
	if literal not in literalTable:
		literalTable[literal]=LiteralField(literal)

def refine(instruction):
	instruction = instruction.upper()
	instruction = removeComments(instruction)
	instruction = list(instruction.split())
	return instruction

def breakInstruction(instruction):
	pass

#Opening file and initializing line, symbol, literal and opcode
path = input("Enter file path: ")
path = "./Sample_Inputs/"+path+".txt"
f = open(path,'r')

instruction = f.readline()
while instruction:
	if instruction=="END":
		break
	if(len(instruction)==1):          #check for empty lines
		instruction = f.readline()
	
	instruction =refine(instruction)
	
	foundMacroDefinition=checkMacro(instruction)
	if(foundMacroDefinition):
		s=''
		name=instruction[0]
		for i in range(2,len(instruction)):      ## find out all the parameters of the macro
			s.append(instruction[i])
		s=s.replace(' ','')
		parameters=list(s.split(','))
		addMacro(instruction[0],parameters)
		instruction=f.readline()
		while(!checkMacro(instruction)):
			macroTable[name].instructionTable.append(instruction)
			instruction=refine(instruction)
			lab=getLabel(instruction)
			if lab!=False:
				macroTable[name].labels.append(lab)
				LabelTable.add()


	# 	add_to_macroTable(instruction)

	
	else:
		instruction = [bin12(num_ins)]+instruction
		instructions.append(instruction)
		
		if(containsLabel(instruction[1])):
			addLabel(instruction[1][0:-1], instruction[0])
		
		if(containsLiteral(instruction)):
			print()
			addLiteral(returnLiteral(instruction))

		num_ins+=1
	instruction=f.readline()

print(instructions)
print(symbolTable)
print(literalTable)



#############pseudocode
##declare END found variable
##make a new file
#while instruction is available and END is not encountered:
##if intruction empty line
###skip line
##if end
###break
## is instruction a comment
###if yes remove comments

## is instruction macro definition
###put macro definition in dictionary
###while mend is not encountered
####add the instruction to macro table/dictionary
####nextline
####if mend is not encountered at all then throw error

##what is the length of the instruction

##does instruction[0] have a label of the form li:
###is label new?
####if yes put it in the label tabel
###else throw multiple definition error

###in this case instruction[1] is opcode remaining is operand
###else instruction[0] is opcode, remaining is operand

##how many operands does the instruction have
##which opcode does the instruction have
###is the opcode a valid opcode
###does the num of operands match the required numebr of operands for your opcode
####if both yes put it in opcode table
####write the instruction in a file
####if no throw incorrect number of operands error
###elseif is it a call to a macro
###if yes put the parameters in a list
###go to macro table and iterate over its instructions
####substitute fields with given parameters
####write substituted instruction in a file
####put the opcode in the opcode table
####put label in label table
##else throw opcode undefined error

#if mendencountered==false:
##throw endnotencountered error

##else throw undefined address

##macros can have local labels



####keep in mind#######
##for add,mul,lac,dsp and sub operand should be a defined address or a constant (not undefined address)
##brn , brz, brp should have a defined valid label (pass 2)
##sac,inp should have a defined or undefined address (not a constant)
##div should have first as defined address or constand, second and third can be defined or undefined address but not a constant


