__author__ = 'tianzhichen'


f = open('yelp_academic_dataset.json','r')

f2 = open('small_yelp_dataset.json','w')
for index, line in enumerate(f):
    if index % 30 == 0:
        f2.write(line)

f.close()
f2.close()
