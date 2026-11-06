import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Салон РИО — Аналитика", page_icon="✂️", layout="wide"
)

st.title("📊 Интерактивный дашборд сети салонов «РИО»")
st.markdown("---")

DATA_URL = "data.csv"


@st.cache_data
def load_data(url):
    try:
        # Читаем файл с разделителем ТАБУЛЯЦИЯ (\t), так как он так сохранился
        df = pd.read_csv(url, sep=r"\t", engine="python", on_bad_lines="skip")

        # Очищаем названия столбцов от лишних пробелов и кавычек
        df.columns = df.columns.str.strip().str.replace('"', "")

        # Точные имена столбцов из вашей ошибки: 'название салона' и 'Сумма'
        addr_col = "название салона"
        sum_col = "Сумма"

        if sum_col not in df.columns or addr_col not in df.columns:
            st.error(
                f"Ошибка структуры! Доступные столбцы: {list(df.columns)}"
            )
            return None

        # Переименовываем столбцы для удобства работы кода
        df = df.rename(columns={sum_col: "Сумма", addr_col: "Адрес"})

        # Очищаем данные в столбце Сумма (удаляем пробелы, валюту) и переводим в числа
        df["Сумма"] = df["Сумма"].astype(str).str.replace(r"[^\d.]", "", regex=True)
        df["Сумма"] = pd.to_numeric(df["Сумма"], errors="coerce").fillna(0)

        return df
    except Exception as e:
        st.error(f"Ошибка при разборе файла: {e}")
        return None


df = load_data(DATA_URL)

if df is not None:
    total_revenue = df["Сумма"].sum()
    total_transactions = len(df)
    unique_salons = df["Адрес"].nunique()

    # Верхние карточки с метриками
    col1, col2, col3 = st.columns(3)
    col1.metric("Общая выручка", f"{total_revenue:,.0f} ₽".replace(",", " "))
    col2.metric("Количество услуг", f"{total_transactions}")
    col3.metric("Активных точек", f"{unique_salons}")

    st.markdown("---")

    # Группировка выручки по салонам
    df_grouped = (
        df.groupby("Адрес")["Сумма"].sum().reset_index()
    )
    df_grouped = df_grouped.sort_values(by="Сумма", ascending=False)

    # Построение круговой диаграммы
    fig = px.pie(
        df_grouped,
        values="Сумма",
        names="Адрес",
        title="Доля выручки по адресам салонов",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu,
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Выручка: %{value:,.0f} ₽<extra></extra>",
    )

    # Отображение графиков и таблиц на экране
    chart_col, table_col = st.columns(2)

    with chart_col:
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        st.subheader("Выручка детально")
        df_table = df_grouped.copy()
        df_table["Сумма"] = df_table["Сумма"].map("{:,.0f} ₽".format)
        st.dataframe(df_table, use_container_width=True, hide_index=True)
