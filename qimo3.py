import requests
from lxml import etree
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import streamlit as st
from collections import Counter

# 设置matplotlib默认字体为SimHei，以支持中文显示
plt.rcParams['font.sans-serif'] = ['SIMHEI']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 定义数据清洗函数
def clean_text(text):
    text = text.replace('\n', '')
    text = text.replace(' ', '')
    text = text.strip()
    return text

# 爬取课程信息
def get_hbnu_course_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html = etree.HTML(response.text)
        courses = html.xpath('//table//tr')[1:]
        result = []
        for index, course in enumerate(courses, start=1):
            seq = str(index)
            name = course.xpath('./td[3]/a/text()')[0].strip() if course.xpath('./td[3]/a') else '无链接的课程名称'
            level = course.xpath('./td[4]/text()')[0].strip()
            year = course.xpath('./td[5]/text()')[0].strip()
            department = course.xpath('./td[6]/text()')[0].strip() if course.xpath('./td[6]/text()') else ''
            teacher = course.xpath('./td[7]/text()')[0].strip()
            clicks = course.xpath('./td[8]/text()')[0].strip()
            result.append([seq, name, level, year, department, teacher, clicks])
        df = pd.DataFrame(result, columns=['序号', '课程名称', '获奖级别', '获奖年度', '所属院系', '课程负责人', '点击次数'])
        df['序号'] = pd.to_numeric(df['序号'])
        df = df.sort_values(by='序号')
        return df
    else:
        st.error("Failed to retrieve the webpage")
        return None

# 生成词云图
def generate_wordcloud(words):
    wordcloud = WordCloud(font_path="C:/Windows/Fonts/msyh.ttc", width=800, height=400, background_color='white').generate(' '.join(words))
    return wordcloud

# 数据可视化分析函数
def visualize_data(df):
    # 课程点击次数分布
    st.subheader("课程点击次数分布")
    plt.figure(figsize=(10, 6))
    plt.barh(df['课程名称'], df['点击次数'], color='skyblue')
    plt.xlabel('点击次数')
    plt.title('课程点击次数分布')
    st.pyplot(plt)

    # 获奖级别分布
    st.subheader("获奖级别分布")
    level_counts = df['获奖级别'].value_counts()
    plt.figure(figsize=(8, 6))
    plt.pie(level_counts, labels=level_counts.index, autopct='%1.1f%%')
    plt.title('获奖级别分布')
    st.pyplot(plt)

    # 课程名称词云
    st.subheader("课程名称词云")
    all_names = ' '.join(df['课程名称'].dropna().astype(str).tolist())
    wordcloud = generate_wordcloud(all_names.split())
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('课程名称词云')
    st.pyplot(plt)

    # 课程名称词频统计
    st.subheader("课程名称词频统计")
    word_counts = Counter(all_names.split())
    df_word_counts = pd.DataFrame(word_counts.items(), columns=['课程名称', '词频'])
    st.dataframe(df_word_counts)

# 主函数
def main():
    st.set_page_config(page_title="课程信息分析工具", page_icon="📊", layout="wide")

    st.title("📊 课程信息分析工具")
    st.write("请输入学院的网址，我们将为您提取课程信息，并展示词频统计和可视化分析。")

    url = st.text_input('输入学院网址:', '')

    if st.button('开始分析'):
        if url:
            st.write("正在分析，请稍候...")
            df = get_hbnu_course_info(url)
            if df is not None:
                visualize_data(df)
                st.success("分析完成！")
        else:
            st.warning("请输入有效的网址")

if __name__ == "__main__":
    main()
