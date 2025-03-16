# CMEE 2024 HPC excercises R code HPC run code proforma

rm(list=ls()) # good practice 
source("yw4524_HPC_2024_main.R")
# it should take a faction of a second to source your file
# if it takes longer you're using the main file to do actual simulations
# it should be used only for defining functions that will be useful for your cluster run and which will be marked automatically

# do what you like here to test your functions (this won't be marked)
# for example
species_richness(c(1,4,4,5,1,6,1))
# should return 4 when you've written the function correctly for question 1

# you may also like to use this file for playing around and debugging
# but please make sure it's all tidied up by the time it's made its way into the main.R file or other files.

print(question_1())

print(question_2())

print(question_5()) 

print(question_6()) 

print(question_14()) 

print(question_18()) 

print(question_22())

print(process_neutral_cluster_results())
print(plot_neutral_cluster_results())

print(challenge_A())

print(challenge_B())

print(challenge_C())

print(challenge_D())

print(challenge_E())