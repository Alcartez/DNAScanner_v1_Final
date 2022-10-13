from flask_wtf import FlaskForm
from wtforms import TextAreaField, EmailField, BooleanField, SubmitField, IntegerField
from flask_wtf.file import FileField
import pandas as pd
import itertools

def VariableGenerator(length ,string):
    nucleotides = ["A" , "T", "G" , "C"]
    iterproduct = itertools.product(nucleotides, repeat = length)
    list = [''.join(iterproduct) for iterproduct in iterproduct]
    var_list = []
    for item in list:
        variable = str(item+string)
        var_list.append(variable)

    return var_list

class FastaForm(FlaskForm):
    fasta_text = TextAreaField('Enter Nucleotide Sequence in Fasta Field')
    fasta_file = FileField('Choose File')
    email = EmailField('Email')
    windowWidth = IntegerField("Enter Window Width")
    submit = SubmitField("Submit")

param_file_2 = "Parameter_Files/Parameter_Files_Trinucleotide - Sheet1.csv"
param_file_1 = "Parameter_Files/Parameter_Sheet_Dinucleotide - Sheet1.csv"
dinucleotide_list = VariableGenerator(2,"") 
trinucleotide_list = VariableGenerator(3,"") 


parameters = {
    'Dinucleotide' : pd.read_csv(param_file_1).columns.values.tolist()[1:],
    'Trinucleotide' : pd.read_csv(param_file_2).columns.values.tolist()[1:],
    'Dinucleotide Rules' : dinucleotide_list, 
    'Trinucleotide Rules' : trinucleotide_list 
}