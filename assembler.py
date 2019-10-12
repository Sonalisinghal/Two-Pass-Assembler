from opcodes import opcodes,opcode_arguments
import copy
import sys

########################FIRST PASS######################
'''
Errors handled in first pass:
 1. Multiple macro definitions
 2. Invalid Label name (Label cannot have a macro name in it and it cannot be an opcode name)
 3. Multiple label definitions
 4. Address supplied should be lesser than 12 bits=4096.
 5. Incorrect number of parameters supplied in a macro
 6. Not enough space for complete program
 7. Incorrect number of parameters supplied for an opcode
 8. END of program not found
 9. MEND/ENDM for macro not found
10. Invalid opcode name/Macro name
11. Unidentified symbol used in a macro
12. Defined label names cannot be used as variable names and vice versa

'''
#########classes required#########
exceptionFlag=False
class LiteralField:
	def __init__(self,literal):
		self.value=literal.replace("'","")
		self.size=1
		i=1
		while(((2**((12*i)-1)//2)-1)<abs(float(self.value))):      #if the constant value is very large, allocate it more memory spaces
			self.size+=1
			i+=1
		self.physicalAdd=None
	def printThis(self):
		print("Value:",self.value,", Size:",self.size,", Physical Address:",self.physicalAdd)

class LabelField:
	def __init__(self,virtualAdd,code): #code = the function that the label belongs to main or name of macro
		self.virtualAdd=virtualAdd
		self.physicalAdd=None
		self.code=code
	def printThis(self):
		print("V.Add:",self.virtualAdd,", P.Add:",self.physicalAdd,", Code:",self.code)

class SymbolField:
	def __init__(self):
		self.physicalAdd=None
		self.status='undefined'
	def printThis(self):
		print("P.Add:",self.physicalAdd,", Status:",str(self.status))

class MacroField:
	def __init__(self,macroparameters):
		self.macroparameters=macroparameters
		self.instructionTable=[]
		self.labels=[]
	def printThis(self):
		print("Parameters:",str(self.macroparameters),", Labels:",str(self.labels))
		print("Instruction Table:")
		for i in self.instructionTable:
			print(str(i))

#########Initialization#########
dataTable={}
labelTable = {}
literalTable = {}
macroTable = {}
symbolTable={}
instructionTable=[]
macroCallcount={}    #stores the number of calls for each macro present in the macro table
LoadAddress = 0		#stores the physical address to load instructions
instructions = []
num_ins = -1                      #counter to count number of instructions
foundMacroDefinition=False       #flag to check if a macro is being defined

#########Functions#########

def printTables():      # prints all the tables generated
	print("\nPrinting instruction table")
	printInstructionTable()
	print("\nPrinting macro table")
	printMacroTable()
	print("\nPrinting label table")
	printLabelTable()
	print("\nPrinting symbol table")
	printSymbolTable()
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
def printSymbolTable():
	for i in symbolTable:
		print(i)
		symbolTable[i].printThis()
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

def checkMacro(instruction):    #Check if a macro has been declared or it has ended
	if len(instruction)>=2:
		if("MACRO" in instruction[1]):
			return True

	if("MEND" in instruction or "ENDM" in instruction) and len(instruction)==5:
		return False

def addMacro(macro,fields):   #Add macro to Macro table
	if macro not in macroTable:
		macroTable[macro]=MacroField(fields)
		macroCallcount[macro]=0
	else:
		global exceptionFlag
		exceptionFlag=True
		print("Error in instruction",macro,*fields)
		print("Exception: MACRO ",macro," has been defined more than once.")
		sys.exit()

def getLabel(instruction):    #Returns label if present in the instruction
	if instruction[0].find(':')!=-1:
		return instruction[0][:-1]
	return False

def addLabel(label, address,code,instruction): #Adds detected label to label table
	global exceptionFlag
	if label in symbolTable:
		exceptionFlag=True
		print("Error in instruction",*instruction)
		print("Exception: Label",label," has also been used as a Variable.")

	else:
		if label not in opcodes:           #check if label name is not a opcode name
			hasMacroName=False
			if code=="Main":
				for x in macroTable.keys():       #check if label name is not a macro name
					if label.find(x)!=-1:
						hasMacroName=True
				if hasMacroName==True:
					exceptionFlag=True
					print("Error in instruction",*instruction)
					print("Exception: Label",label,"is invalid as labels cannot have same name as a MACRO.")
					sys.exit()
			if label not in labelTable:        #check if label is not defined more than once
				labelTable[label]=LabelField(address,code)
			else:
				exceptionFlag=True
				print("Error in instruction",*instruction)
				print("Exception: Label",label,"has been defined more than once.")
				sys.exit()
		else:
			exceptionFlag=True
			print("Error in instruction",*instruction)
			print("Exception: Label cannot be an opcode name.",label,"is an opcode name.")
			sys.exit()

def addData(parameters,opcode):       #Adds the parameters in the datatable and literal table
	global exceptionFlag
	for i in range(len(parameters)):
		x=getLiteral(parameters[i])             #if literal found, add it to the literal table
		if x!=False:
			addLiteral(x)
		else:
			if (opcode in ["INP","ADD","SUB","LAC","SAC","DSP","MUL","DIV"]):       ##as for branch, labels will be supplied which are already handled
				try:
					parameters[i]=int(parameters[i])
					if parameters[i] not in dataTable:
						if -1<parameters[i]<4096:
							if opcode=="INP" or opcode=="SAC":
								dataTable[parameters[i]]="defined"
							# if opcode=="SAC" and len(instructionTable)>0:     ##if we consider that cla should result to 0 value, in which case store 0 would be a defined address
							# 	if instructionTable[-1][-1]=="CLA":
							# 		dataTable[i]="defined"
							else:
								dataTable[parameters[i]]="undefined"
						else:
							exceptionFlag=True
							print("Error in instruction",opcode,*parameters)
							print("Exception: Address supplied exceeds memory limit. It should be lesser than 12 bits, that is 4096. Address",i,"is not a valid address.")
							# sys.exit()
				except:
					if (opcode in ["INP","ADD","SUB","LAC","SAC","DSP","MUL","DIV"]): 
						if parameters[i] not in labelTable:
							if parameters[i] not in symbolTable:
								symbolTable[parameters[i]]=SymbolField()
								if(opcode in ["INP","SAC"]):
									symbolTable[parameters[i]].status = "defined"
						else:
							exceptionFlag=True
							print("Error in instruction",opcode,*parameters)
							print("Exception:",opcode,"cannot take labels as parameters")

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
	global exceptionFlag
	macroCallcount[name]+=1
	newLabelnames=[]
	for i in macroTable[name].labels:        #creates new label name set for the macro of the form macroName-
		newLabelnames.append(str(name)+str(i)+str(macroCallcount[name]))
	
	copiedInstructionset=copy.deepcopy(macroTable[name].instructionTable)
	if len(parameters)!=len(macroTable[name].macroparameters):
		exceptionFlag=True
		print("Error in instruction",name,*parameters)
		print("Exception: Macro",name,"takes",len(macroTable[name].macroparameters),"parameters but",len(parameters),"were given.")
		sys.exit()
	for instruction in copiedInstructionset:
		vAddress=getVirtualAddress(num_ins)             
		label=getLabel(instruction)
		if label!=False:
			instruction[0]=newLabelnames[macroTable[name].labels.index(label)]+":"
			addLabel(newLabelnames[macroTable[name].labels.index(label)],vAddress,name,instruction)
			opcodeFrom=1
		else:     
			opcodeFrom=0
		
		opcode=instruction[opcodeFrom]
		for i in range(opcodeFrom+1,len(instruction)):
			if instruction[i] in macroTable[name].labels:       #if label found, substitute it with the new label
				instruction[i]=newLabelnames[macroTable[name].labels.index(instruction[i])]
			elif (instruction[i] in macroTable[name].macroparameters):
				instruction[i]=parameters[macroTable[name].macroparameters.index(instruction[i])]     #substitute macro parameters with actual parameters
			else:
				exceptionFlag=True
				print("Error in instruction",*instruction)
				print("Exception: Unidentified symbol",instruction[i],"in MACRO",name+".")
				sys.exit()
		if opcode in opcodes:                           #check if correct number of operands are supplied in the macro
			if len(instruction[opcodeFrom+1:])==opcode_arguments[opcode]:
				addData(instruction[opcodeFrom+1:],opcode)
				instructionTable.append([vAddress]+[instruction])
			else:
				exceptionFlag=True
				print("Error in instruction",*instruction)
				print("Exception:",opcode,"takes",opcode_arguments[opcode],"arguments but",len(instruction[opcodeFrom+1:]),"were given.")
				sys.exit()
		else:
			exceptionFlag=True
			print("Error in instruction",*instruction)
			print("Exception:",opcode,"is not a valid opcode name.")
			sys.exit()
		num_ins+=1

	return num_ins-1


#########Main code#########
path = input("Enter file path: ")
path = "./Sample_Inputs/"+path    #Opening file and initializing line, symbol, literal and opcode
f = open(path+".txt",'r')
endEncountered=False
instruction = f.readline()
while instruction:
	if instruction=="END" or instruction=="END\n":            #if end is encountered, stop execution
		endEncountered=True
		break
	if(len(instruction)==1):          #check for empty lines
		instruction = f.readline()
		continue
	instruction =refine(instruction)
	if len(instruction)==0:             #check if the line is just a comment
		instruction = f.readline()
		continue
	if instruction[0]=='START':
		if(len(instruction)==2):
			LoadAddress = instruction[1]
		instruction = f.readline()
		continue
	
	#Add macros to macro table
	foundMacroDefinition=checkMacro(instruction)       #check if instruction is a macro
	if(foundMacroDefinition):
		s=''
		name=instruction[0]
		for i in range(2,len(instruction)):      #Find out all the parameters of the macro
			s=s+instruction[i]
		s=s.replace(' ','')
		parameters=list(s.split(','))
		addMacro(instruction[0],parameters)
		instruction=f.readline()
		while(checkMacro(instruction)!=False):
			if (not instruction):        #If end of file appears without getting MEND or END
				# exceptionFlag=True
				print("Exception: MEND/ENDM not specified after Macro definition",name)
				sys.exit()
			if(len(instruction)==1):          #check for empty lines
				instruction = f.readline()
				continue
			if ("MACRO" in instruction or "END" in instruction):   #If another macro is declared or end of file appears
				print("Exception: MEND/ENDM not specified after Macro definition",name)
				sys.exit()
			instruction=refine(instruction)
			if len(instruction)==0:             #check if the line is just a comment
				instruction = f.readline()
				continue
			macroTable[name].instructionTable.append(instruction)     #append all the instructions to macro's instruction table
			labelsPresent=getLabel(instruction)                       #if the macro contains label, add them to the macros label table
			if labelsPresent!=False:
				if labelsPresent not in macroTable[name].labels:
					macroTable[name].labels.append(labelsPresent)
				else:
					exceptionFlag=True
					print("Error in instruction",*instruction)
					print("Exception: Label",labelsPresent,"has been defined multiple times for macro",name)   #if the label is declared multiple times in a macro
					sys.exit()
			instruction=f.readline()
		instruction=f.readline()

	else:	
		num_ins+=1
		vAddress=getVirtualAddress(num_ins)
		label=getLabel(instruction)
		if(label!=False):    #label is present
			addLabel(label, vAddress,"Main",instruction)
			opcodeFrom=1
		else:
			opcodeFrom=0
		opcode=instruction[opcodeFrom]
		parameters=instruction[opcodeFrom+1:]
		if opcode in macroTable:
			num_ins=handleMacroCalls(opcode,parameters,num_ins)
			
		elif opcode in opcodes:
			if len(parameters)==opcode_arguments[opcode]:
				addData(parameters,opcode)
				instructionTable.append([vAddress]+[instruction])
			else:
				exceptionFlag=True
				print("Error in instruction",*instruction)
				print("Exception: Opcode",opcode,"takes",opcode_arguments[opcode],"arguments but",len(parameters),"were given.")
				sys.exit()
		else:
			exceptionFlag=True
			print("Error in instruction",*instruction)
			print("Exception:",opcode,"is not a valid opcode or a macro name.")
			sys.exit()
		instruction=f.readline()

if endEncountered==False:
	exceptionFlag=True
	print("Exception: END of program not found. Please declare 'END' command at the end of the assembly program.")
	sys.exit()
if exceptionFlag==False:
	print('######## SUCCESS: First pass ended successfully ########')
#printTables()


########################SECOND PASS######################
def getOffset(num_ins):
	'''
	Input parameters: Number of instructions present in instruction table.

	Returns: Offset/Starting address for instruction table, to be stored 
	in a contiguous memory space.

	Throws "Not enough space" exception if instruction table size is larger
	than available memory, or if a contiguous memory space cannot be found.

	'''
	totalIns=num_ins+1
	dataset=list(dataTable.keys())
	dataset=sorted(dataset)
	#maxInstructionSize=0
	offset=False
	if(len(dataset)>1):
		for i in range(1,len(dataset)):
			if (dataset[i]-dataset[i-1]>totalIns):
				offset=dataset[i-1]+1
				break
	if(len(dataset)==1):
		if((dataset[-1]+num_ins+1)<4096):
			offset = dataset[-1]+1
	if(len(dataset)==0):
		offset = 0
		return(offset)
	if (offset==False and len(dataset)!=0):
		if((dataset[-1]+num_ins+1)<4096):
			offset = dataset[-1]+1
	if offset==False:
		global exceptionFlag
		exceptionFlag=True
		print("Exception: Not enough space for complete program")
		sys.exit()
	else:
		return offset

def addOffset(offset):
	'''
	Input: Offset calculated for binding of instructions and labels.

	Operation: Maps the instructions and labels in Instruction Table and Label Table to
	physical addresses by adding offset
	'''
	for i in range(0,len(instructionTable)):
		instructionTable[i][0] = bin12(int(instructionTable[i][0],2)+offset)
	for j in labelTable:
		labelTable[j].physicalAdd = bin12(int(labelTable[j].virtualAdd,2)+offset)

def getLiteralPool(offset,num_ins):
	'''
	Input: offset for Instruction table and total number of instructions.

	Returns: Offset/Starting address for literal pool, to be stored 
	in a contiguous memory space.

	Throws "Not enough space" exception if literal pool is larger
	than available memory, or if a contiguous memory space cannot be found.
	'''
	totalMem = 0
	startAdd = False
	for i in literalTable:
		totalMem+=literalTable[i].size
	occAddresses=list(dataTable.keys())
	for j in range(0,num_ins):
		occAddresses+=[j+offset]
	occAddresses = sorted(occAddresses)
	for k in range(1,len(occAddresses)):
		if (occAddresses[k]-occAddresses[k-1]>totalMem):
			startAdd=occAddresses[k-1]+1
			break
	if startAdd==False:
		if((occAddresses[-1]+totalMem+1)<4096):
			startAdd = occAddresses[-1]+1
	if startAdd==False:
		global exceptionFlag
		exceptionFlag=True
		print("Exception: Not enough space for complete program")
		sys.exit()
	else:
		return startAdd

def assignLiteralPool(startAdd):
	'''
	Input: Starting address for literal pool

	Operation: Assigns physical addresses for literals for binding.
	'''
	nextAdd = startAdd
	for i in literalTable:
		literalTable[i].physicalAdd = []
		for j in range(0,literalTable[i].size):
			literalTable[i].physicalAdd+=[nextAdd]
			nextAdd+=1
	return(nextAdd)

def getSymbolPool(offset,literalPoolAdd,nextAdd,num_ins):
	'''
	Input: offset for Instruction table, literal pool starting and ending addresses,
	total number of instructions.

	Returns: Offset/Starting address for variables in symbol table, to be stored 
	in a contiguous memory space.

	Throws "Not enough space" exception if variable pool is larger
	than available memory, or if a contiguous memory space cannot be found.
	'''
	totalMem = len(symbolTable)
	startAdd = False
	occAddresses = list(dataTable.keys())
	for i in range(0,num_ins):
		occAddresses+=[i+offset]
	for j in range(literalPoolAdd,nextAdd):
		occAddresses+=[j]
	occAddresses=sorted(occAddresses)
	for k in range(1,len(occAddresses)):
		if(occAddresses[k]-occAddresses[k-1]>totalMem):
			startAdd=occAddresses[k-1]+1
			break
	if startAdd==False:
		if((occAddresses[-1]+totalMem+1)<4096):
			startAdd = occAddresses[-1]+1
	if startAdd==False:
		global exceptionFlag
		exceptionFlag=True
		print("Exception: Not enough space for complete program")
		sys.exit()
	else:
		return(startAdd)

def assignSymbolPool(startAdd):
	'''
	Input: Starting address for variable pool

	Operation: Assigns physical addresses for variables for binding.
	'''
	nextAdd = startAdd
	for i in symbolTable:
		symbolTable[i].physicalAdd = nextAdd
		nextAdd+=1
	return(nextAdd)

def removeLabelDefinitions():
	'''
	Operation: Removes label declarations from the instruction table
	for conversion to machine language.
	'''
	for i in range(0,len(instructionTable)):
		if(instructionTable[i][1][0].find(":")!=(-1)):
			del instructionTable[i][1][0]

def checkOperands():
	'''
	Operation: Checks validity of operands corresponding to opcodes.
	ADD, MUL, LAC, SUB: Only have defined variables/addresses or literals.
	DSP: Only has defined variable/address.
	BRN, BRP, BRZ: Only have defined label.
	SAC, INP: Only have defined/undefined variables/addresses
	DIV: Only has first operand as defined variable/address or literal, second and third operands as 
	defined/undefined variables/addresses 
	'''
	global exceptionFlag
	for i in range(0,len(instructionTable)):
		instruction = instructionTable[i][1]
		code = instructionTable[i][1][0]
		if(code=='ADD' or code=='MUL' or code=='LAC' or code=='DSP' or code=='SUB'):
			if(instruction[1] in symbolTable):
				if(symbolTable[instruction[1]].status=='undefined'):
					exceptionFlag=True
					print("Error in instruction",*instruction)
					print("Exception: "+code, "cannot have undeclared variable as operand.")
					sys.exit()
			elif(instruction[1] in literalTable):
		 		pass
			elif(dataTable[int(instruction[1])]=='undefined'):
		 		exceptionFlag=True
		 		print("Error in instruction",*instruction)
		 		print("Exception: "+code, "cannot have undefined address as operand.")
		 		sys.exit()
		if(code=="DSP"):
			if(instruction[1] in symbolTable):
				pass
			if(instruction[1] in literalTable):
				print("Error in instruction",*instruction)
				print("Exception: "+code, "cannot have literal as operand.")
				sys.exit()
		if(code=='BRN' or code=='BRP' or code=='BRZ'):
			if(instruction[1] not in labelTable):
				exceptionFlag=True
				print("Error in instruction",*instruction)
				print("Exception: "+code, "has an undeclared label: "+instruction[1]+" as operand.")
				sys.exit()
		if(code=='SAC' or code=='INP'):
			if(instruction[1] in literalTable):
				exceptionFlag=True
				print("Error in instruction",*instruction)
				print("Exception: "+code, "can only have address/variable as operand.")
				sys.exit()
		if(code=='DIV'):
			if(instruction[1] in symbolTable):
				if(symbolTable[instruction[1]].status=='undefined'):
					exceptionFlag=True
					print("Error in instruction",*instruction)
					print("Exception: "+code, "cannot have undeclared variable as operand.")
					sys.exit()
			elif(instruction[1] in literalTable):
				pass
			elif(dataTable[int(instruction[1])]=='undefined'):
				exceptionFlag=True
				print("Error in instruction",*instruction)
				print("Exception: "+code, "should have first operand as address/variable or constant. "+instruction[1]+" is an undefined address.")
				sys.exit()
			if(instruction[2] in literalTable or instruction[3] in literalTable):
				exceptionFlag=True
				print("Error in instruction",*instruction)
				print("Exception: "+code, "should have second and third operands as valid addresses/variables.")
				sys.exit()

def convertOpcodes():
	'''
	Operation: Convert opcodes in instruction table to machine language.
	'''
	for i in range(0,len(instructionTable)):
		instruction = instructionTable[i][1]
		code = instructionTable[i][1][0]
		instructionTable[i][1][0] = opcodes[code]

def convertOperands():
	'''
	Operation: Convert operands to the physical adresses they are bound to.
	'''
	for i in range(0,len(instructionTable)):
		instruction = instructionTable[i][1]
		for k in range(1,len(instruction)):
			if(instruction[k] in labelTable):
				instructionTable[i][1][k] = labelTable[instruction[k]].physicalAdd
			elif(instruction[k] in literalTable):
				instructionTable[i][1][k] = bin12(literalTable[instruction[k]].physicalAdd[0])
			elif(instruction[k] in symbolTable):
				instructionTable[i][1][k] = bin12(symbolTable[instruction[k]].physicalAdd)
			elif(int(instruction[k]) in dataTable):
				instructionTable[i][1][k] = bin12(int(instruction[k]))

def writeToFile():
	'''
	Operation: Write generated machine code to text file named:
	<sample_file>_output.txt
	Splits machine code into blocks of four bits for readability.
	'''
	f = open(path+"_output.txt","w+")
	for i in range(0,len(instructionTable)):
		instruction = instructionTable[i][1]
		s = ''
		for k in range(0,len(instruction)):
			s+=instruction[k]
		l = (len(s))
		block = 0
		machine_ins = ''
		while(block!=l):
			machine_ins+=s[block:block+4]+" "
			block+=4
		machine_ins+="\n"
		f.write(machine_ins)
		print(machine_ins)
	f.close()


############MAIN CODE##############
literalPoolAdd = 0
variablePoolAdd = 0
nextAdd = 0
offset = getOffset(num_ins)
addOffset(offset)
if(len(literalTable)!=0):
	literalPoolAdd = getLiteralPool(offset,num_ins)
	nextAdd = assignLiteralPool(literalPoolAdd)
if(len(symbolTable)!=0):
	variablePoolAdd = getSymbolPool(offset,literalPoolAdd,nextAdd,num_ins)
	assignSymbolPool(variablePoolAdd)
removeLabelDefinitions()
checkOperands()
if exceptionFlag==False:
	print('######## SUCCESS: Second pass ended successfully ########')
	convertOpcodes()
	convertOperands()
	writeToFile()
	printTables()

print(LoadAddress)