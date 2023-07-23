import argparse
import json
import re
import os
import base64
import streamlit as st
from random import choice


def read_articles(filename):
    """
    读取题库文件
    :param filename: 题库文件名
    :return: 一个字典，题库内容
    """
    with open(filename, 'r', encoding="utf-8") as f:
        # TODO: 用 json 解析文件 f 里面的内容，存储到 data 中
        data = json.load(f)

    return data


def replace(article, keys):
    """
    替换文章内容
    :param article: 文章内容
    :param keys: 用户输入的单词
    :return: 替换后的文章内容
    """
    for i in range(len(keys)):
        # TODO: 将 st.session_statearticle 中的 {{i}} 替换为 keys[i]
        # hint: 你可以用 str.replace() 函数，也可以尝试学习 re 库，用正则表达式替换
        article = re.sub(
            r'\{\{' + str(i+1) + r'\}\}', f"<span style='color:orange;font-weight:bold'>{keys[i]}</span>",  article)
    return article


def download_json(object):
    json_str = json.dumps(object, ensure_ascii=False, indent=4)
    with open("data.json", "w", encoding="utf-8") as f:
        f.write(json_str)
    with open("data.json", "r", encoding="utf-8") as f:
        data = f.read()
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="data.json">Download JSON file</a>'
    st.markdown(href, unsafe_allow_html=True)


# 创建一个下载按钮，使用户可以通过点击该按钮来下载 Markdown 文件
def download_md(md_str):
    with open("data.md", "w", encoding="utf-8") as f:
        f.write(md_str)
    with open("data.md", "r", encoding="utf-8") as f:
        data = f.read()
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:text/markdown;base64,{b64}" download="data.md">Download your article as Markdown file</a>'
    st.markdown(href, unsafe_allow_html=True)


st.set_page_config(layout="wide")
st.title("Ahyd's 「文章填词」小游戏")
with st.sidebar:
    files = os.listdir('.')
    jsons = []
    for file in files:
        if '.json' in file:
            jsons.append(file)
    jsons.append('自定义文章')
    filename = st.selectbox("#### 请选择文章所在路径", [
                            None]+jsons, format_func=lambda x: '...' if x is None else x)
if filename:
    if filename != '自定义文章':
        data = read_articles(filename)
        if data:
            articles = data["articles"]
            st.subheader("可选题目：")
            titles = []
            for cur in data["articles"]:
                st.write("- " + cur['title'])
                titles.append(cur["title"])
            with st.sidebar:
                chose = st.checkbox('指定文章题目')
                if chose:
                    title = st.selectbox("#### 请选择文章题目", titles)
                    for cur in articles:
                        if cur["title"] == title:
                            st.session_state.obj = cur
                            break
                else:
                    rand = st.button("随机抽取文章")
                    if rand:
                        cur = choice(articles)
                        st.session_state.obj = cur
    else:
        with st.sidebar:
            obj = {}
            obj['title'] = st.text_input('请输入文章标题')
            obj['article'] = st.text_input('请输入要替换的文章正文\n\n换行请输入<br/>')
            hints_str = st.text_input("请以 ' , ' 为间隔符输入hints")
            obj['hints'] = hints_str.split(',')
            add_image = st.checkbox('添加图片')
            if add_image:
                obj['image'] = st.text_input("请输入图片链接")
            st.session_state.obj = obj
    if 'obj' in st.session_state:
        obj = st.session_state.obj
        st.write("文章题目：", obj["title"])
        if filename == '自定义文章':
            st.write("要替换的文章正文：<br/>", obj['article'], unsafe_allow_html=True)
        hints = obj["hints"]
        input = []
        button = False
        with st.sidebar:
            if obj['title'] and obj['article'] and obj['hints'] != ["",]:
                with st.form('input_form'):
                    for i in range(len(hints)):
                        input.append('')
                        input[i] = st.text_input(hints[i])
                    button = st.form_submit_button('确认')
        if button:
            st.write('### 「'+obj['title']+'」:')
            article = replace(
                obj['article'], input)
            st.write(article, unsafe_allow_html=True)
            download_json(obj)
            download_md(article)
            if 'image' in obj:
                st.image(obj['image'])


if (not filename) or ('obj' not in st.session_state):
    st.write("### 简介")
    st.markdown('''
                **文章填词** 是一个⼗分简单的⼩游戏。
                - 具体来说，出题者事先准备好一篇文章，并将其中的一些单词挖去；
                - 对于挖去的单词，出题者会给一定提示，例如该词的词性、褒贬、类型等；
                - 做题者看不到文章，只能根据提示随意选择单词；
                - 最终将做题者给定的单词填回原文，往往会达成不错的喜剧效果。
                - 你可以和他⼈⽐拼，谁能填出最正常/无厘头的文章，同时，这也能作为学习外语、拓宽词汇量的途径。
                ''')

    st.write("#### 例子：")
    st.code('''
    中文题目：
    我们都爱 {{1}} 这门课程。
    这门课程是多么的 {{2}}，以至于所有人都在课程上认真地 {{3}}。
    在设计数字电路时,我们需要运用到逻辑门、半导体存储器等知识。
    这些内容相互联系,共同构成复杂的数字电路。
    这门课能启发我们的逻辑思维能力和科学思考能力。
    通过为难我们的练习和作业,我们的理解能力和解决问题的能力得到了提高。
    这些将对今后的 {{4}} 和工作有很大益处。

    单词限制：
    1. 教材名称    2. 形容词   3. 动词，与学生相关  4. 你最喜欢做的事情
    
    填空可能是：
    1. 《数字逻辑电路》 2. 青涩    3. 内卷      4. 玩原神
            ''')
