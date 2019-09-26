from opcodes import opcodes

labelTable = {}
symbolTable = {}
literalTable = {}
opcodeTable = {}

def containsLabel(line):
	if(line.find(":")!=-1):
		return(True)
	else:
		return(False)

path = input("Enter file path: ")
path = "./Sample_Inputs/"+path
f = open(path,'r') #first pass
line = f.readline()

while line:
	'''
	instruction=list(line.split())
	if len(instruction)<2:
		instruction.insert(0,'')
		print(instruction)
	'''
	print(line)
	line=f.readline()
	if(containsLabel(line)):
		print(list(line.split()))
	else:
		print(list(line.split()))
