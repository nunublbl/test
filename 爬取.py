import requests
import csv

csv_file = open('articles.csv', 'w', newline='', encoding='utf-8')
writer = csv.writer(csv_file)
writer.writerow(['标题', '链接', '摘要'])

offset = 0
while True:
    url = 'https://www.zhihu.com/api/v4/members/zhang-jia-wei/articles'
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
    params = {
        'include': 'data[*].comment_count,suggest_edit,is_normal,thumbnail_extra_info,thumbnail,can_comment,comment_permission,admin_closed_comment,content,voteup_count,created,updated,upvoted_followees,voting,review_info,is_labeled,label_info;data[*].author.badge[?(type=best_answerer)].topics',
        'offset': str(offset),
        'limit': '20',
        'sort_by': 'created'
    }

    res = requests.get(url, params=params, headers=headers)
    resjson = res.json()
    articles = resjson['data']
    for article in articles:
        title = article['title']
        link = article['url']
        excerpt = article['excerpt']
        writer.writerow([title, link, excerpt])

    offset += 20
    if offset > 40:
        break
    # if resjson['paging']['is_end'] == True:
    #     break
csv_file.close()
import requests
import time

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}


def errwarning():
    print('输入有误，请重新输入')


def step1():
    global category
    url = 'https://www.shanbay.com/api/v1/vocabtest/category/?_=1584538302210'
    res = requests.get(url, headers=headers)
    datas = res.json()['data']
    while True:
        try:
            num = int(input(
                '第 1 步，请选择出题范围(选择对应的数字) 1.GMAT，2.考研，3.高考，4.四级，5.六级，6.英专，7.托福，8.GRE，9.雅思，10.任意：'))
            if num not in range(1, 11):
                errwarning()
            else:
                break
        except:
            errwarning()
    category = datas[num-1][1]
    return datas[num-1][0]


def vocabularies():
    url = 'https://www.shanbay.com/api/v1/vocabtest/vocabularies/?category={}&_=1584542288515'.format(
        step1())
    res = requests.get(url, headers=headers)
    datas = res.json()['data']
    return datas


def show_words():
    datas = vocabularies()
    for i in range(len(datas)):
        print(str(i+1)+'.'+datas[i]['content'], end='， ')
        if i+1 in range(11, 51, 10):
            print('')
    return datas


def step2():
    datas = show_words()
    isnotend = True
    while isnotend:
        knownums = []
        nums = input('\n第 2 步，请选择你认识的单词(选择对应的数字，以\",\"分隔，全选请输入0)：')
        nums_list = nums.split(',')
        for num in nums_list:
            try:
                if int(num) in range(1, len(datas)+1):
                    knownums.append(int(num)-1)
                elif int(num) == 0:
                    knownums = []
                    for i in range(0, 50):
                        knownums.append(i)
                    isnotend = False
                    break
                else:
                    errwarning()
                    break
            except:
                errwarning()
                break
        else:
            isnotend = False
    return knownums, datas


def step3():
    knowwords = []
    notknowwords = []
    rightwords = []
    wrongwords = []
    knownums, datas = step2()
    print('第 3 步，单词测试')
    for i in range(len(datas)):
        data = datas[i]
        pk = data['pk']
        if i in knownums:
            definition_choices = data['definition_choices']
            print(data['content'])
            for k in range(4):
                print(str(k+1)+'. '+definition_choices[k]['definition'])
            print('5. 不认识')
            while True:
                try:
                    num = int(input('请选择正确的词义(选择对应的数字)：'))
                    if num not in range(1, 6):
                        errwarning()
                    else:
                        break
                except:
                    errwarning()
            if num == 5:
                print('')
                notknowwords.append(data)
            if num in range(1, 5):
                knowwords.append(data)
                if definition_choices[num-1]['pk'] == pk:
                    print('bingo\n')
                    rightwords.append(data)
                else:
                    print('oh no\n')
                    wrongwords.append(data)
        else:
            notknowwords.append(data)
    return knowwords, notknowwords, rightwords, wrongwords, datas


def result():
    knowwords, notknowwords, rightwords, wrongwords, datas = step3()
    right_ranks = ''
    for r in range(len(rightwords)):
        if r == 0:
            right_ranks = str(rightwords[r]['rank'])
        else:
            right_ranks = right_ranks+','+str(rightwords[r]['rank'])

    word_ranks = ''
    for d in range(len(datas)):
        if d == 0:
            word_ranks = str(datas[d]['rank'])
        else:
            word_ranks = word_ranks+','+str(datas[d]['rank'])

    url = 'https://www.shanbay.com/api/v1/vocabtest/vocabularies/'
    data = {
        'right_ranks': right_ranks,
        'word_ranks': word_ranks
    }
    res = requests.post(url, headers=headers, data=data)

    vocab = res.json()['data']['vocab']
    print('你的词汇量大约是:{}'.format(vocab))
    print('{}{}个词汇，不认识{}个，认识{}个，掌握{}个，错了{}个'.format(
        category, len(datas), len(notknowwords), len(knowwords), len(rightwords), len(wrongwords)))
    f = open('生词本.txt', 'a+')
    f.write(time.strftime("%Y/%m/%d %H:%M:%S\n"))
    newwords = notknowwords+wrongwords
    for i in range(len(newwords)):
        data = newwords[i]
        for choice in data['definition_choices']:
            if choice['pk'] == data['pk']:
                f.write('{}. {}: {}\n'.format(
                    i+1, data['content'], choice['definition']))
    f.write('\n')
    f.close()
    print('生词本已更新，请前往本地文件夹查看')


result()