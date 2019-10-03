from opcodes import opcodes

symbolTable = {}
literalTable = {}
opcodeTable = {}
instructions = []
num_ins = 0

bin8 = lambda x : ''.join(reversed([str((x >> i) & 1) for i in range(8)] ) )

def containsLabel(token): #Checks for presence of label in first token of instruction
	if(token.find(":")!=-1):
		return(True)
	else:
		return(False)

def addLabel(label, address): #Adds detected label to symbol table
	symbolTable[label]=address

#def addVariable():
#	pass

def addLiteral(literal): #Adds literals to Literal Table
	literalTable[literal] = literal[1:-1]

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

#def containsVariable(instruction): #Checks if passed instruction contains variables
#	for token in instruction:


def containsLiteral(instruction): #Checks if passed instruction contains literals
	for token in instruction:
		if(token[0]=="'" and token[-1]=="'"):
			return(True)
		else:
			return(False)

def returnLiteral(instruction):
	for token in instruction:
		if(token[0]=="'" and token[-1]=="'"):
			return(token)


#Opening file and initializing line, symbol, literal and opcode
path = input("Enter file path: ")
path = "./Sample_Inputs/"+path+".txt"
f = open(path,'r')

instruction = f.readline()
while instruction:
	instruction = removeComments(instruction)
	instruction = list(instruction.split())
	instruction = [bin8(num_ins)]+instruction
	instructions.append(instruction)
	
	if(containsLabel(instruction[1])):
		addLabel(instruction[1][0:-1], instruction[0])
	#if(containsVariable(instruction)):
	#	pass
	if(containsLiteral(instruction)):
		print()
		addLiteral(returnLiteral(instruction))

	num_ins+=1
	instruction=f.readline()

print(instructions)
print(symbolTable)
print(literalTable)
