text="hi there hello world dump tex"
count=0
for i in text:
    if i==" ":
        count+=1
    else:
        continue
# this might seem like an brute force but it only does counts
# the space the last word in text wont have the space at end so it will be neglected.
print(count)

# using split method
def word_count(text):
    count=len(text.split())
    return count

path='textfile.txt'
with open(path,'r') as file:
    # with ensure that file will be closed after the use and even if the exception occurs
    content=file.read()

print(word_count(content))

