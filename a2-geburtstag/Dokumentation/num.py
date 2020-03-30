nums = {1:1}

for n in range(2, 20):
    # print("n", n)
    s = 0
    for i in range(1,(n//2)+1):
        # print("i", i)
        s += 5*nums[i]*nums[n-i]+1
    nums[n] = s

for i in nums.keys():
    print(i, "&", '{:,}'.format(nums[i]).replace(',','.') , "\\\\ \\hline")
