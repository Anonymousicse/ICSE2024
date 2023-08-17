# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 13:42:57 2020

@author: Yinxing Xue
"""
import sys
import os
import math

from nen.DescribedProblem import DescribedProblem
from nen.util.moipProb import MOIPProblem

class DimacsMOIPProblem(MOIPProblem):  
    """
    define the DIMACS reader of a MOBIP SPLC problem
    """
    def __init__(self, projectName):  
        "read from the external Dimacs files"
        objectNames, featureNames, attributeNames, objectives, sparseInequations, sparseInequationSenses, sparseEquations = DimacsMOIPProblem.readDimacsFiles(projectName)
        "call the father class constructor"
        MOIPProblem.__init__(self, len(objectNames), len(featureNames), len(attributeNames))  
        self.load(objectives, sparseInequations, sparseEquations, False, None)
        self.objectNames=objectNames
        self.featureNames=featureNames
        self.sparseInequationSensesList = sparseInequationSenses
        
        self.attributeMatrix =self.__private_convertDenseLise__(self.objectiveSparseMapList)
        if  len(objectives) != self.objectiveCount or len(featureNames)!= self.featureCount:
            raise Exception('input not consistent', 'eggs')
        self.reOrderObjsByRange()
        self.convertInequation2LeConstr()
        
    @classmethod
    def readDimacsFiles(cls, projectName):
    
        #this is a map to store the objective names: index-objective 
        objectNames = {}
 
        #this is a map to store the feature names: index-name 
        featureNames = {}

        #this is a map to store the attribute names: index-attribute  
        attributeNames = {}
        
         
        #each sparse map is to represent one objectives, and use the list to store all the objectives maps
        objectiveSparseMapList = [] 
    
        #each sparse map is to represent one constraint in inequation, and use the list to store all the inequation constraints
        #NOTE That it is for the less than <=, the key is the index, the value is the cofficient, and the rhs(righside value) is the last index 
        """
        NOTE That  the key is the index, the value is the cofficient, and the rhs(righside value) is the last index 
        for example: 
        x_1 - 2* x_2 <= 1
        shoule be 
        {0:1, 1: -2, 2: 1} --- where 0 is for x_1, 1 is for x_2, 2 is for rhs
        """
        sparseInequationsMapList = [] 
        
        #each item in the list is the operation for the above objectiveSparseMapList[]
        # for example :  'G' refers >=, 'L' refers <=
        sparseInequationSensesList = [] 
    
        #each sparse map is to represent one constraint in equation, and use the list to store all the equation constraints
        sparseEquationsMapList = []   
        
        #read from the old dimacs file 
        inputPath = os.path.join(DescribedProblem.RAW_DATA_PATH, 'FSP\\{name}.dimacs'.format(name=projectName)).replace("\\","/")
        totalFea = 0
        f= open(inputPath)
        line = f.readline()
        while line:
            #print (line)
            if line.strip()=='':
                line = f.readline()
                continue
            if line.startswith("p cnf ")== True: 
                break
            parts = line.split(" ")
            if parts[1].endswith('$'):
                parts[1] = parts[1].replace('$',"")
            if parts[0]=="c"  and parts[1].isnumeric(): 
                index = int(parts[1].strip())
                featureNames[index-1] =  parts[2].strip()               
            line = f.readline()
        f.close()
        #print (featureNames)
        
        #read from the simplified dimacs file 
        inputNewPath = os.path.join(DescribedProblem.RAW_DATA_PATH, 'FSP\\{name}.dimacs.new'.format(name=projectName)).replace("\\","/")
        totalInequal=0
        f= open(inputNewPath)
        line = f.readline()
        while line:
            #print (line)
            if line.strip()=='':
                line = f.readline()  
                continue
            line = line.replace("\n","")
            line = line.strip()
            parts = line.split(" ")
            if line.startswith("p cnf ")== True: 
                totalFea = int(parts[2].strip())
                totalInequal = int(parts[3].strip())   
            else:
                counter=0
                ineqlDict={}
                #The number of features that are negated 
                numNegatedFeas = 0
                # -41 -43 0	means 	ms EXC min
                # -41 -43 0	means 	!ms OR !min == True
                # 1-x_41 + 1- x_43 >=1  
                # and we further infer it as -x_41 -x_43  >= 1 -2 (#(!features))
                for fea in parts:
                    counter= counter+1
                    if counter==len(parts):
                        fea = fea.rstrip()  
                    index=  int(fea) #convert to index                   
                    if index >0 and counter< len(parts) :  #if negative or positive
                        ineqlDict[index-1] = 1
                    elif index <0 and counter< len(parts) : 
                        index= abs(index)
                        ineqlDict[index-1] = -1
                        numNegatedFeas+=1
                    elif(counter==len(parts) and index==0): #if reaching the end of the constraint
                        ineqlDict[len(featureNames)] = 1- numNegatedFeas
                        continue
                    elif (counter==len(parts) and index!=0):
                        raise Exception('dimacs format error', 'eggs')
                        os._exit(0) 
                sparseInequationsMapList.append(ineqlDict)
                sparseInequationSensesList.append('G')
            line = f.readline()
        f.close()
        #print (sparseInequationsMapList)
                  
        #read from the mandatory features of the dimacs file
        inputMandFPath = os.path.join(DescribedProblem.RAW_DATA_PATH, 'FSP\\{name}.dimacs.mandatory'.format(name=projectName)).replace("\\","/")
        f= open(inputMandFPath)
        line = f.readline()
        while line:
            #print (line)
            if line.strip()=='':
                line = f.readline()
                continue
            eqlDict={}
            if line.strip().isnumeric(): 
                index= int(line.strip())
                eqlDict[index-1] = 1
                eqlDict[len(featureNames)] = 1  #feature value is 1, must be selected
            sparseEquationsMapList.append(eqlDict)
            line = f.readline()
        f.close()
        
        #read from the dead features of the dimacs file
        inputDeadFPath = os.path.join(DescribedProblem.RAW_DATA_PATH, 'FSP\\{name}.dimacs.dead'.format(name=projectName)).replace("\\","/")
        f= open(inputDeadFPath)
        line = f.readline()
        while line:
            #print (line)
            if line.strip()=='':
                line = f.readline()
                continue
            eqlDict={}
            if line.strip().isnumeric(): 
                index= int(line.strip())
                eqlDict[index-1] = 1
                eqlDict[len(featureNames)] = 0 #feature value is 0, must be deselected
            sparseEquationsMapList.append(eqlDict)
            line = f.readline()
        f.close()
        #print (sparseEquationsMapList)
         
        #read from the augments of the dimacs file
        inputAugPath = os.path.join(DescribedProblem.RAW_DATA_PATH, 'FSP\\{name}.dimacs.augment'.format(name=projectName)).replace("\\","/")
        if projectName == "RealAmazon":
            DimacsMOIPProblem.ReadAmazonFM(projectName,inputAugPath)   
        elif projectName == "RealDrupal":
            DimacsMOIPProblem.ReadRealFM(projectName,inputAugPath)   
        else:
            attributeNames,objectNames, objectiveSparseMapList = DimacsMOIPProblem.ReadNormalFM(projectName,inputAugPath)
 
        """
        Note that 
        """
        assert len(featureNames)==totalFea
        
        assert len(sparseInequationsMapList)==totalInequal
        assert len(sparseInequationsMapList)==len(sparseInequationSensesList)
        return objectNames, featureNames, attributeNames, objectiveSparseMapList, sparseInequationsMapList,sparseInequationSensesList, sparseEquationsMapList
    
    @classmethod
    def ReadNormalFM(cls, projectName,inputAugPath):    
        temAttributeNames=[]
        tempObjectNames= []
        tempObjectiveSparseMapList = []
        f= open(inputAugPath)
        line = f.readline()
        while line:
            #print (line)
            if line.strip()=='':
                line = f.readline()
                continue
            #handle the line head " #FEATURE_INDEX COST USED_BEFORE DEFECTS"
            if line.startswith("#FEATURE_INDEX "):
                attributes = line.strip().split(" ")
                attributes[0] = attributes[0].replace("#","")
                temAttributeNames.extend(attributes)
                counter=0
                for attr in attributes:
                    if counter!= 0:
                        tempObjectNames.append("#"+attr)
                    else: 
                        tempObjectNames.append("#Deselected")
                    tempObjectiveSparseMap={}
                    tempObjectiveSparseMapList.append(tempObjectiveSparseMap)
                    counter+=1
            #handle the line inside like "1 5.2 1 0"
            else:
                augments = line.strip().split(" ")
                index= int(augments[0])
                counter=0
                for augment in augments:
                    tempObjectiveSparseMap = tempObjectiveSparseMapList[counter]
                    #if it is the sum of deselected fea
                    if counter==0: 
                        tempObjectiveSparseMap[index-1]=-1
                    # else if it is about used_before, we need to negate between [0,1] to make it not_used_before
                    elif  counter==2: 
                        tempObjectiveSparseMap[index-1]=1-float(augment)
                    else:
                        tempObjectiveSparseMap[index-1]=float(augment)
                    counter+=1
            line = f.readline()
        f.close()
        #print (temAttributeNames)
        #print (tempObjectNames)
        #print (tempObjectiveSparseMapList)
        return temAttributeNames,tempObjectNames, tempObjectiveSparseMapList
           
    @classmethod
    def ReadRealFM(cls, projectName,inputAugPath):  
        return 
    
    @classmethod
    def ReadAmazonFM(cls, projectName,inputAugPath):  
        return

    def __private_convertDenseLise__(self,objectiveSparseMapList):
        listLength = len(objectiveSparseMapList)
        matrix =  [[] for i in range(listLength)]
        for i in range(listLength):
            dictionary = objectiveSparseMapList[i]
            matrix[i] = [0.0]* len(dictionary)
            for key in dictionary:
                matrix[i][key]=dictionary[key]
        return matrix
    
    @classmethod
    def convertRslt2OldFormat(cls, cplexParetoSet, featureSetSize, outPath):  
        """converting results format for ease of comparison with SATIBEA and other methods

        Converting the results format. The original objective order in tuple of CplexResult is: 
            '#COST, -1*#FEATURE, #USED_BEFORE, #DEFECTS'
            and the wanted format is '#Deselected_FEATURE,#USED_BEFORE, #DEFECTS,#COST'
    
        Args:
            cplexParetoSet: the original cplex result sets
            featureSetSize: the size of the features of the MOIP problems
            outPath: path to print out the newCplexParetoSet
            
        Returns:
            newCplexParetoSet: the new cplex result sets with the wanted objective order
            
        Raises:  IOError: An error occurred 
        """
        newCplexParetoSet=set()
        for cplexRslt  in cplexParetoSet:
            numDeselectedFea= featureSetSize+cplexRslt[1]
            newTuple=(numDeselectedFea, cplexRslt[2], cplexRslt[3], cplexRslt[0])
            newCplexParetoSet.add(newTuple)
        os.makedirs(os.path.dirname(outPath), exist_ok=True)
        file = open(outPath,"w+") 
        #file.write(';'.join(list(map(str,self.cplexParetoSet)))) 
        for cplexRslt in newCplexParetoSet:
            set2floatList = [str(x) for x in cplexRslt]
            resultString =' '.join(set2floatList)
            file.write(resultString+"\n")
        file.close() 
        return newCplexParetoSet
    
if __name__ == "__main__":

    prob = DimacsMOIPProblem('WebPortal')  
    # prob.displayObjectiveCount()
    # prob.displayFeatureCount()
    prob.displayObjectives()
    prob.displayObjectiveSparseMapList()
    prob.displayVariableNames()
    prob.displaySparseInequationsMapList()
    prob.displaySparseInequationSenseList()
    prob.displaySparseEquationsMapList()
    #prob.displayAttributeMatrix()
# else:
#     print("dimacsMoipProb.py is being imported into another module")