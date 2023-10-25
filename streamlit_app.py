import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objs as go
import io
import plotly.express as px
from streamlit_elements import dashboard
from streamlit_elements import elements, mui, html
from PIL import Image


# 接收xls格式數據
st.set_page_config(page_title="總產出可視化", page_icon="📈")
logo = Image.open(r'C:\Users\asus\Desktop\中陽實業\LOGO.png')
st.sidebar.image(logo, width=120)
st.title('自動化報表')
NG_file = st.sidebar.file_uploader("上傳不良回饋歷史記錄", type=['xls', 'xlsx'])
uploaded_file = st.sidebar.file_uploader("上傳產出歷程報表", type=["xls", "xlsx"])
machine_file = st.sidebar.file_uploader("上傳機台數據", type=["xls", "xlsx"])

# 各廠區機台編號
if machine_file is not None:
    mach = pd.read_excel(machine_file)

# 不良品數據清洗
if NG_file is not None:
    data_ng = pd.read_excel(NG_file)
    cols = data_ng.columns

# 数据清洗
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    # 創建數據清洗方式
    genre = st.radio("是否清理數據", ["保持原檔😎", "數據報表🚀"])

    path = st.text_input("請輸入你預先想將數據放入的文件夾") # r'C:\Users\asus\Desktop\中陽實業'

    if genre == "保持原檔😎":
        st.write(df)
        file_name_gen = st.checkbox("下載數據", key="file_name_gen", disabled=False)
        if path:
            if file_name_gen:
                name = st.text_input("輸入文件名稱")
                if st.button('生成文件'):
                    excel_path = path + "\\" + name + ".xlsx"
                    df.to_excel(excel_path, index=False)
                    st.success(f"報告已生成: {excel_path}")
                    st.balloons()
        else:
            st.warning("必須指定數據放置文件夾")
    elif genre == "數據報表🚀":
        # 更換名稱
        change = st.checkbox("更改數據名稱", key="name", disabled=False)
        # 将所有NA值替换成0
        zero = st.checkbox("將所有NA值替換為0", key="NA")
        # 剔除製造部門
        drop = st.checkbox("剔除重複的部門名稱以及大夜班數據", key="depart")
        # NG狀態歸一化
        wash = st.checkbox("NG數據歸一化")
        # 指定日期範圍產出報表
        range_date = st.checkbox("選擇日期範圍報表", key="range_d")
        # 指定日期產出報表
        spec = st.checkbox("選擇指定日期報表", key="special")
        # 不良回饋歷史記錄
        NG_state = st.checkbox("NG數據交叉分析", key="NG")


        if change:
            df.rename(columns={'天': '總產出', '早': '日產出', '夜': '夜產出'}, inplace=True)
        if zero:
            df = df.fillna(0)
        if drop:
            df = df.drop(columns=['部門名稱', '大夜'])
        if wash:
            data_ng['歸屬日期'] = pd.to_datetime(data_ng['歸屬日期'])
            data_ng['狀態'] = data_ng['狀態'].replace('更新(刪除)', '刪除')
            data_ng['狀態'] = data_ng['狀態'].replace('更新', '新增')
            cols = ['產品料號', '工序', '工序名稱','機台',
                    '工單', '產出數', '狀態','作業人員', '歸屬日期',
                    '不良原因', '不良數量', '回饋人員']

            data_ng = data_ng.groupby(['產品料號', '工序', '工序名稱',
                                            '機台', '工單', '作業人員',
                                            '歸屬日期', '不良原因', '回饋人員']).agg({'不良數量': 'sum'}).reset_index()
        if range_date:
            # 日期范围选择
            min_date = pd.to_datetime(df["製造日"].min()).date()
            max_date = pd.to_datetime(df["製造日"].max()).date()

            selected_start_date = st.date_input("選擇起始日期", min_value=min_date, max_value=max_date, value=min_date, key="start")
            selected_end_date = st.date_input("選擇结束日期", min_value=min_date, max_value=max_date, value=max_date, key="end")

            # 根据用户选择的日期范围过滤数据
            f_data = df[(df['製造日'].dt.date >= selected_start_date) & (df['製造日'].dt.date <= selected_end_date)]

            # 使用selectbox选择品名
            selected_product = st.selectbox("選擇品名", f_data['品名'].unique(), key="product1")
            product_data = f_data[f_data['品名'] == selected_product]

            # 使用selectbox选择工序
            selected_process = st.selectbox("選擇工序", product_data['工序'].unique(), key="num1")
            process_data = product_data[product_data['工序'] == selected_process]

            # 加總該工序在時間段内產出
            total_output = process_data['總產出'].sum()


            tab11, tab12, tab13, tab14, tab15= st.tabs([f"{selected_product}-{selected_process}產出數據",
                                                        f"{selected_product}-{selected_process}可視化",
                                                        f"{selected_product}機台NG分佈",
                                                        "工序產出漏斗圖",
                                                        "所有機台NG分佈"])
            process_data['製造日'] = process_data['製造日'].dt.date

            data_ng = data_ng[(data_ng['歸屬日期'].dt.date >= selected_start_date) & (
                    data_ng['歸屬日期'].dt.date <= selected_end_date)]
            # data = data_ng[cols]

            tab11.subheader("數據内容")
            tab11.write(process_data)
            # 時間範圍内NG數據
            # tab11.write(data_ng)
            with tab11:
                file_name_range = st.checkbox("下載數據", key="file_name_range", disabled=False)
                if path:
                    if file_name_range:
                        name1 = st.text_input("輸入文件名稱")
                        if name1:
                            if st.button('生成文件'):
                                excel_path = path + "\\" + name1 + ".xlsx"
                                process_data.to_excel(excel_path, index=False)
                                st.success(f"報告已生成: {excel_path}")
                                st.balloons()
                        else:
                            st.warning("請輸入文件名稱")
                else:
                    st.warning("必須指定數據放置文件夾")
            with tab12:
                tab12.subheader("時間序列可視化")
                tab12.bar_chart(
                    process_data.set_index('製造日')[['總產出', '日產出', '夜產出']])  # product_data.set_index('製造日')['總產出']
            with tab13:
                NG_product = data_ng[data_ng['產品料號'].isin(process_data['料號'])]  #process_data['產品料號'].isin(product_data['料號'].tolist())
                fig_pie1 = px.pie(NG_product, names='不良原因', values='不良數量',
                                  title=f'{selected_start_date}-{selected_end_date}-'
                                        f'{selected_product}不良原因分佈')
                st.plotly_chart(fig_pie1)
                st.dataframe(NG_product)
            # 指定品名產出漏斗圖
            with tab14:
                # 收集所选品名（selected_product）下的所有工序的数据
                product_data = f_data[f_data['品名'] == selected_product]

                # 创建漏斗图
                fig_funnels = go.Figure()

                for process in product_data['工序'].unique():
                    process_output = product_data[product_data['工序'] == process]
                    fig_funnels.add_trace(go.Funnel(
                        name=f"{process} (總產出: {process_output['總產出'].sum()})",# str(process)
                        y=process_output['工序'],
                        x=process_output['總產出'],
                    ))

                fig_funnels.update_layout(
                    title=f"{selected_product}各工序產出漏斗图",
                )

                # 在tab14中显示漏斗图
                tab14.subheader(f"{selected_product}各工序產出漏斗图")
                st.plotly_chart(fig_funnels)

            # 時間範圍内NG機台圓餅圖/數據提取
            with tab15:
                fig_pie = px.pie(data_ng, names='不良原因', values='不良數量', title=f'{selected_start_date}-{selected_end_date} 不良原因分佈')
                st.plotly_chart(fig_pie)
                st.dataframe(data_ng)
                # 下載數據
                file_NGname_range = st.checkbox("下載數據", key="file_NGname_range", disabled=False)
                if path:
                    if file_NGname_range:
                        name2 = st.text_input("輸入文件名稱")
                        if name2:
                            if st.button('生成文件'):
                                excel_path = path + "\\" + name2 + ".xlsx"
                                data_ng.to_excel(excel_path, index=False)
                                st.success(f"報告已生成: {excel_path}")
                                st.balloons()
                        else:
                            st.warning("請輸入文件名稱")
                else:
                    st.warning("必須指定數據放置文件夾")

        if spec:
            # 選擇指定日期
            selected_date = st.date_input("選擇日期")
            # 根據選擇的日期篩選數據
            s_data = df[(df['製造日'].dt.date == selected_date)]

            # 單日機台數據
            F1 = mach['1F廠區'].count()
            F2 = mach['2F廠區'].count()
            F3 = mach['F2廠區'].count()

            tab31, tab32, tab33, tab34 = st.tabs(["1F廠區", "2F廠區", "F2廠區", "各廠使用率圓餅圖"])
            with tab31:
                f1 = s_data[s_data['機台'].isin(mach['1F廠區']) & (s_data['總產出'] != 0)]
                st.write(f"日期: {selected_date}")
                st.write(f"1F廠區機台總數: {F1}")
                st.write(f"1F廠區選定日期的運行機台數: {len(f1)}")
                st.write("1F廠區選定日期的機台數據:")
                st.write(f1)

            with tab32:
                f2 = s_data[s_data['機台'].isin(mach['2F廠區']) & (s_data['總產出'] != 0)]
                st.write(f"日期: {selected_date}")
                st.write(f"2F廠區機台總數: {F2}")
                st.write(f"2F廠區選定日期的運行機台數: {len(f2)}")
                st.write("2F廠區選定日期的機台數據:")
                st.write(f2)

            with tab33:
                f3 = s_data[s_data['機台'].isin(mach['F2廠區']) & (s_data['總產出'] != 0)]
                st.write(f"日期: {selected_date}")
                st.write(f"F2廠區機台總數: {F3}")
                st.write(f"F2廠區選定日期的運行機台數: {len(f3)}")
                st.write("F2廠區選定日期的機台數據:")
                st.write(f3)

            with tab34:
                # 計算圓餅圖的數據
                pie_data = pd.DataFrame({
                    '廠區': ['1F廠區', '2F廠區', 'F2廠區'],
                    '機台數': [len(f1), len(f2), len(f3)]
                })
                fig_pie = px.pie(pie_data, names='廠區', values='機台數', title=f'各廠機台使用率圓餅圖 ({selected_date})')
                st.plotly_chart(fig_pie)


            # f1 = s_data[s_data['機台'].isin(mach['1F廠區']) & (s_data['總產出'] != 0)].shape[0]
            # f2 = s_data[s_data['機台'].isin(mach['2F廠區']) & (s_data['總產出'] != 0)].shape[0]
            # f3 = s_data[s_data['機台'].isin(mach['F2廠區']) & (s_data['總產出'] != 0)].shape[0]
            #
            # # 準備數據
            # data = pd.DataFrame({'廠區': ['1F廠區', '2F廠區', 'F2廠區'],
            #                      '機台數': [F1, F2, F3]})
            #
            # # 使用 Plotly Express 創建圓餅圖
            # fig = px.pie(data, names='廠區', values='機台數', title=f'各廠區機台數 ({selected_date})')
            #
            # # 顯示圖表
            # st.plotly_chart(fig)

            # 使用selectbox选择品名
            selected_Product = st.selectbox("選擇品名", s_data['品名'].unique(), key="product2")
            product_Data = s_data[s_data['品名'] == selected_Product]

            # 使用selectbox选择工序
            selected_Process = st.selectbox("選擇工序", product_Data['工序'].unique(), key="num2")
            process_Data = product_Data[product_Data['工序'] == selected_Process]
            # 選擇x,y坐標
            chose_x = st.multiselect("選擇當日需要分析時間軸", s_data.columns, default=['08','09','10','11','12','13',
                                                                                    '14','15','16','17','18','19',
                                                                                    '20','21','22','23','00','01',
                                                                                    '02','03','04','05','06','07'])
            total_Output = process_Data['總產出'].sum()

            tab21, tab22, tab23 = st.tabs(["數據", "可視化", "產出加總"])
            s_data['製造日'] = s_data['製造日'].dt.date

            tab21.subheader("數據内容")
            tab21.write(process_Data)
            with tab21:
                file_name_spec = st.checkbox("下載數據", key="file_name_spec", disabled=False)
                if path:
                    if file_name_spec:
                        name2 = st.text_input("輸入文件名稱", key="name2")
                        if name2:
                            if st.button('生成文件', key='2'):
                                excel_path = path + "\\" + name2 + ".xlsx"
                                process_Data.to_excel(excel_path, index=False)
                                st.success(f"報告已生成: {excel_path}")
                                st.balloons()
                        else:
                            st.warning("請輸入文件名稱")
                else:
                    st.warning("必須指定數據放置文件夾")

            tab22.subheader("時間序列可視化")
            with tab22:
                if chose_x:
                    # 使用 Plotly 创建时间序列图表，每个机台一条折线
                    fig = go.Figure()
                    for machine in process_Data['機台'].unique():
                        machine_data = process_Data[process_Data['機台'] == machine]
                        machine_data = machine_data.drop(columns=['料號','品名','工序','製造日','總產出','日產出','夜產出'])
                        # 从machine_data中获取所选的x和y值
                        x_values = machine_data.columns  # 使用所有列作为x值
                        y_values = machine_data.iloc[0].values  # 使用第一行的数据作为y值

                        fig.add_trace(
                            go.Scatter(x=x_values, y=y_values, mode='lines', name=machine)
                        )
                    st.plotly_chart(fig)
                else:
                    tab22.warning("請選擇時間點。")
            tab23.subheader("異常展示")
            tab23.write("總產出：" + str(total_Output))
            with tab23:
                length = len(process_Data)
                average = total_Output / length
                st.write("一共有" + str(length) + "個數據")

                sum_M = 0
                machine_empty = []
                # machine_empty = {"機台": []}

                for i in range(len(process_Data)):
                    if process_Data['總產出'].iloc[i] < average or process_Data['總產出'].iloc[i] == 0:
                        sum_M = sum_M + 1
                        machine_empty.append(process_Data.iloc[i])
                        # machine_empty["機台"].append(process_Data.iloc[i].to_dict())  # process_Data['機台'].iloc[i]

                length1 = len(machine_empty)
                st.write("一共有" + str(length1) + "個異常數據")
                st.write("低於平均產出的機台：")
                st.dataframe(machine_empty)
                st.write("低於平均產出的機台數量：", sum_M)


                # if chose_x:
                #     # 将数据进行长格式化
                #     melted_data = process_Data.melt(id_vars=['製造日', '機台'], value_vars=chose_x, var_name='時間點',
                #                                     value_name='產出值')
                #
                #     # 使用 Altair 可视化
                #     chart = alt.Chart(melted_data).mark_line().encode(
                #         x='時間點:T',  # T 表示时间类型
                #         y='產出值:Q',
                #         color='機台:N'
                #     ).properties(
                #         width=800,
                #         height=400
                #     )
                #
                #     st.altair_chart(chart)
                # else:
                #     tab2.warning("請選擇時間點。")
            # chart_data = process_Data[chose_x]
            # tab2.line_chart(chart_data)

        if NG_state:
            cross = st.radio("不良記錄分析", ["人員👨‍🔧", "機台🖥️", "人機分析👨‍🔧🖥️"])
            data_cleaned = data_ng.groupby(['不良原因', '機台', '作業人員'
                                            ]).agg({'不良數量': 'sum'}).reset_index()
            cols = data_cleaned.columns
            if cross == "人員👨‍🔧":
                # 不良原因-機台 / 不良原因-人員
                work = data_cleaned['作業人員'].unique()
                selected_NG = st.selectbox("選擇人員", work, key="NG_people")
                data_Ng_wash1 = data_cleaned[data_cleaned['作業人員']==selected_NG]

                fig_pie = px.pie(data_Ng_wash1, names="不良原因", values='不良數量',
                             title=f'{selected_NG}不良原因分佈')
                st.plotly_chart(fig_pie)
                show_data1 = data_ng[(data_ng['作業人員'] == selected_NG)]

                st.write(show_data1)
            if cross == "機台🖥️":
                # 不良原因-機台 / 不良原因-人員
                mach = data_cleaned['機台'].unique()
                selected_NG = st.selectbox("選擇機台", mach, key="NG_mach")
                data_Ng_wash2 = data_cleaned[data_cleaned['機台']==selected_NG]

                fig_pie = px.pie(data_Ng_wash2, names="不良原因", values='不良數量',
                             title=f'{selected_NG}不良原因分佈')
                st.plotly_chart(fig_pie)
                show_data2 = data_ng[(data_ng['機台'] == selected_NG)]

                st.write(show_data2)
            if cross == "人機分析👨‍🔧🖥️":
                # 不良原因-機台 / 不良原因-人員
                # 使用selectbox選擇人員
                selected_people = st.selectbox("選擇人員", data_cleaned['作業人員'].unique(), key="worker")
                people_data = data_cleaned[data_cleaned['作業人員'] == selected_people]

                # 使用selectbox選擇機台
                selected_mach = st.selectbox("選擇機台", people_data['機台'].unique(), key="mach")
                mach_data = people_data[people_data['機台'] == selected_mach]

                fig_pie = px.pie(mach_data, names="不良原因", values='不良數量',
                             title=f'{selected_people}-{selected_mach}不良原因分佈')
                st.plotly_chart(fig_pie)
                show_data3 = data_ng[(data_ng['作業人員'] == selected_people) & (data_ng['機台'] == selected_mach)]
                st.write(show_data3)
