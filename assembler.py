from opcodes import opcodes

symbolTable = {}
literalTable = {}
opcodeTable = {}
instructions = []
num_ins = 0

bin8 = lambda x : ''.join(reversed([str((x >> i) & 1) for i in range(8)] ) )

def containsLabel(token):
	if(token.find(":")!=-1):
		return(True)
	else:
		return(False)

def addLabel(label, address):
	symbolTable[label]=address	

def containsVariable(instruction):
	pass

def containsLiteral(instruction):
	pass

path = input("Enter file path: ")
path = "./Sample_Inputs/"+path+".txt"
f = open(path,'r')

instruction = f.readline()
while instruction:
	if(instruction.find(";")!=(-1)):
		instruction = instruction[0:instruction.find(";")]
	instruction = list(instruction.split())
	instruction = [bin8(num_ins)]+instruction
	instructions.append(instruction)
	
	if(containsLabel(instruction[1])):
		addLabel(instruction[1][0:-1], instruction[0])
	if(containsVariable(instruction)):
		pass
	if(containsLiteral(instruction)):
		pass

	num_ins+=1
	instruction=f.readline()

print(instructions)
print(symbolTable)