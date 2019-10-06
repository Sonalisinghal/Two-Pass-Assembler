from opcodes import opcodes,opcode_arguments
import copy
import sys
## constant value can have a very big value ie greater than 4096, in such a case give it more memory addresses

########################FIRST PASS######################
'''
Errors handled in first pass:
 1. Multiple macro definitions
 2. Invalid Label name (Label cannot have a macro name in it and it cannot be an opcode name)
 3. Multiple label definitions
 4. Address supplied should be of integer type.
 5. Address supplied should be lesser than 12 bits=4096.
 6. Incorrect number of parameters supplied in a macro
 7. Incorrect number of parameters supplied for an opcode
 8. END not found
 9. MEND/ENDM not found
10. Invalid opcode name/Macro name

'''
#########classes required#########
class LiteralField:
	def __init__(self,literal):
		self.value=literal.replace("'","")
		self.size=1
		i=1
		while(2**(12*i)<float(self.value)):      #if the constant value is very large, allocate it more memory spaces
			self.size+=1
		self.physicalAdd=None
	def printThis(self):
		print(self.value,self.physicalAdd)

class LabelField:
	def __init__(self,virtualAdd,code): #code = the function that the label belongs to main or name of macro
		self.virtualAdd=virtualAdd
		self.physicalAdd=None
		self.code=code
	def printThis(self):
		print(self.virtualAdd,self.physicalAdd)

class MacroField:
	def __init__(self,macroparameters):
		self.macroparameters=macroparameters
		self.instructionTable=[]
		self.labels=[]
	def printThis(self):
		print(str(self.macroparameters),str(self.labels))
		for i in self.instructionTable:
			print(str(i))

#########Initialization#########
dataTable={}
labelTable = {}
literalTable = {}
macroTable = {}
instructionTable=[]
macroCallcount={}    #stores the number of calls for each macro present in the macro table

instructions = []
num_ins = 0                      #counter to count number of instructions
foundMacroDefinition=False       #flag to check if a macro is being defined

#########Functions#########

def printTables():      # prints all the tables generated
	print("\nPrinting instruction table")
	printInstructionTable()
	print("\nPrinting macro table")
	printMacroTable()
	print("\nPrinting label table")
	printLabelTable()
	print("\nPrinting data table")
	printDataTable()
	print("\nPrinting literal table")
	printLiteralTable()
def printMacroTable():
	for i in macroTable:
		print(i)
		macroTable[i].printThis()
def printDataTable():
	print(dataTable)
def printLabelTable():
	for i in labelTable:
		print(i)
		labelTable[i].printThis()
def printInstructionTable():
	for i in instructionTable:
		print(i)
def printLiteralTable():
	for i in literalTable:
		print(i)
		literalTable[i].printThis()

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

	if("MEND" in instruction or "MEND" in instruction) and len(instruction)==5:
		return False

def addMacro(macro,fields):
	if macro not in macroTable:
		macroTable[macro]=MacroField(fields)
		macroCallcount[macro]=0
	else:
		print("Exception: MACRO ",macro," has been defined more than once.")
		sys.exit()

def getLabel(instruction):
	if instruction[0].find(':')!=-1:
		return instruction[0][:-1]
	return False

def addLabel(label, address,code): #Adds detected label to symbol table
	if label not in opcodes:           #check if label name is not a opcode name
		hasMacroName=False
		if code=="Main":
			for x in macroTable.keys():       #check if label name is not a macro name
				if label.find(x)!=-1:
					hasMacroName=True
			if hasMacroName==True:
				print("Exception: Label name ",label,"is invalid as labels cannot have a Macro name in it.")
				sys.exit()
		if label not in labelTable:        #check if label is not defined more than once
			labelTable[label]=LabelField(address,code)
		else:
			print("Exception: Label name ",label," has been defined more than once.")
			sys.exit()
	else:
		print("Exception: Label name cannot be an opcode name.",label,"is a valid opcode name")
		sys.exit()

def addData(parameters,opcode):       #Adds the parameters in the datatable and literal table
	for i in parameters:
		x=getLiteral(i)
		if x!=False:
			addLiteral(x)
		else:
			if (i not in dataTable) and (opcode in ["INP","ADD","SUB","LAC","SAC","DSP","MUL","DIV"] or opcode in macroTable):       ##as for branch, labels will be supplied which are already handled
				try:
					i=int(i)
				except:
					print("Exception: Address supplied should be of integer type.")
					sys.exit()
				if -1<i<4096:
					if opcode=="INP":
						dataTable[str(i)]="defined"
					else:
						dataTable[str(i)]="undefined"
				else:
					print("Exception: Address supplied should be lesser than 12 bits=4096.")
					sys.exit()


def getLiteral(token): #Checks if passed instruction contains literals
	if(token[0]=="'" and token[-1]=="'"):
		return(token)
	return False

def addLiteral(literal): #Adds literals to Literal Table
	if literal not in literalTable:
		literalTable[literal]=LiteralField(literal)

def refine(instruction):  #Case handling and divide the instruction in Labels, opcode and parameters
	instruction = instruction.upper()
	instruction = removeComments(instruction)
	instruction = list(instruction.split())
	return instruction

def getVirtualAddress(num_ins): #Returns a virtual 12-bit binary address for the instruction
	return bin12(num_ins)

def handleMacroCalls(name,parameters,num_ins):   #Expands Macro calls in the assembly program
	# print("macro call encountered for",name,parameters)
	macroCallcount[name]+=1
	newLabelnames=[]
	for i in macroTable[name].labels:        #creates new label name set for the macro of the form macroName-
		newLabelnames.append(str(name)+str(i)+str(macroCallcount[name]))
	
	copiedInstructionset=copy.deepcopy(macroTable[name].instructionTable)
	# print("new label names are",newLabelnames)
	if len(parameters)!=len(macroTable[name].macroparameters):
		print("Exception: Macro",name,"takes",len(macroTable[name].macroparameters),"parameters but",len(parameters),"were given.")
		sys.exit()
	for instruction in copiedInstructionset:
		# print("macro call",instruction)
		vAddress=getVirtualAddress(num_ins)
		label=getLabel(instruction)
		if label!=False:
			instruction[0]=newLabelnames[macroTable[name].labels.index(label)]+":"
			addLabel(newLabelnames[macroTable[name].labels.index(label)],vAddress,name)
			opcodeFrom=1
		else:     
			opcodeFrom=0
		
		opcode=instruction[opcodeFrom]
		for i in range(opcodeFrom+1,len(instruction)):
			if instruction[i] in macroTable[name].labels:
				instruction[i]=newLabelnames[macroTable[name].labels.index(instruction[i])]
			else:
				instruction[i]=parameters[macroTable[name].macroparameters.index(instruction[i])]
		# print("modified macro instruction",instruction)
		if opcode in opcodes:
			if len(instruction[opcodeFrom+1:])==opcode_arguments[opcode]:
				instructionTable.append([vAddress]+[instruction])
				addData(instruction[opcodeFrom+1:],opcode)
			else:
				print("Exception:",opcode,"takes",opcode_arguments[opcode],"arguments but",len(instruction[opcodeFrom+1:]),"were given.")
				sys.exit()
		else:
			print("Exception:",opcode,"is not a valid opcode name.")
			sys.exit()
		num_ins+=1

	return num_ins-1

#########Main code#########
#Opening file and initializing line, symbol, literal and opcode
path = input("Enter file path: ")
path = "./Sample_Inputs/"+path+".txt"
f = open(path,'r')
endEncountered=False
instruction = f.readline()
while instruction:
	# print("main",instruction)
	if instruction=="END\n":            #if end is encountered, stop execution
		endEncountered=True
		break
	if(len(instruction)==1):          #check for empty lines
		instruction = f.readline()
	
	instruction =refine(instruction)
	
	##add macros to macro table
	foundMacroDefinition=checkMacro(instruction)       #check if instruction is a macro
	if(foundMacroDefinition):
		s=''
		name=instruction[0]
		for i in range(2,len(instruction)):      ## find out all the parameters of the macro
			s=s+instruction[i]
		s=s.replace(' ','')
		parameters=list(s.split(','))
		addMacro(instruction[0],parameters)
		instruction=f.readline()
		while(checkMacro(instruction)!=False):
			try:
				if(len(instruction)==1):          #check for empty lines
					instruction = f.readline()
				instruction=refine(instruction)
				# print("appending in macro table",instruction)
				macroTable[name].instructionTable.append(instruction)     #append all the instructions to macro's instruction table
				labelsPresent=getLabel(instruction)                       #if the macro contains label, add them to the macros label table
				if labelsPresent!=False:
					macroTable[name].labels.append(labelsPresent)
				instruction=f.readline()
			except:
				print("Exception: MEND/ENDM not specified after Macro definition",name)
				sys.exit()
		instruction=f.readline()

	else:	
		num_ins+=1
		vAddress=getVirtualAddress(num_ins)
		# print("getting address",vAddress)
		label=getLabel(instruction)
		if(label!=False):    #label is present
			# print("trying to add",label)
			addLabel(label, vAddress,"Main")
			opcodeFrom=1
		else:
			opcodeFrom=0
		opcode=instruction[opcodeFrom]
		parameters=instruction[opcodeFrom+1:]
		if opcode in macroTable:
			num_ins=handleMacroCalls(opcode,parameters,num_ins)
			
		elif opcode in opcodes:
			if len(parameters)==opcode_arguments[opcode]:
				instructionTable.append([vAddress]+[instruction])
				addData(parameters,opcode)
			else:
				print("Exception: Opcode",opcode,"takes",opcode_arguments[opcode],"arguments but",len(parameters),"were given.")
				sys.exit()
		else:
			print("Exception:",opcode,"is not a valid opcode or a macro name.")
			sys.exit()


		instruction=f.readline()

if endEncountered==False:
	print("Exception: END of program not found. Please declare 'END' command at the end of the assembly program")
	sys.exit()
print('######## SUCCESS: First pass ended successfully ########')
printTables()


####keep in mind#######
##for add,mul,lac,dsp and sub operand should be a defined address or a constant (not undefined address)
##brn , brz, brp should have a defined valid label (pass 2)
##sac,inp should have a defined or undefined address (not a constant)
##div should have first as defined address or constand, second and third can be defined or undefined address but not a constant

##the number of parameters supplied to macro = number of parameters supplied during call
