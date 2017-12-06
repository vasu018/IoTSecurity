def merge_list(llist,rlist):
    common=[]
    for i in llist:
        if i in rlist:
            common.append(i)
    if not common:
        return llist+rlist
    merged_list=[]
    lpos=0
    rpos=0
    for i in common:
        lindex = llist.index(i)
        rindex = rlist.index(i)
        if set(llist[lpos:lindex]).intersection(set(rlist[rpos:rindex])):
            return 
        merged_list += llist[lpos:lindex]
        merged_list += rlist[rpos:rindex]
        if i in merged_list:
            return
        merged_list.append(i)
        lpos = lindex+1
        rpos = rindex+1
    if lpos<len(llist):
        merged_list += llist[lpos:len(llist)]
    if rpos<len(rlist):
        merged_list += rlist[rpos:len(rlist)]
    return merged_list

print(merge_list([1,2,3,9,8], [5,2,7,26,3,78,8]))