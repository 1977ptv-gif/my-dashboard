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
        # Пробуем сначала прочитать с разделителем ТОЧКА С ЗАПЯТОЙ (часто для кириллических CSV)
        df = pd.read_csv(
            url, sep=";", quotechar='"', on_bad_lines="skip", encoding="utf-8"
        )

        # Если не получилось и заголовок склеился, пробуем обычную запятую
        if len(df.columns) <= 1:
            df = pd.read_csv(
                url,
                sep=",",
                quotechar='"',
                on_bad_lines="skip",
                encoding="utf-8",
            )

        # Очищаем названия столбцов от невидимых символов и пробелов
        df.columns = df.columns.str.strip().str.replace('"', "")

        # Ищем столбец, который содержит слово 'Сумма'
        sum_col = [c for c in df.columns if "Сумма" in c]
        # Ищем столбец, который содержит слово 'Адрес'
        addr_col = [c for c in df.columns if "Адрес" in c]

        if not sum_col or not addr_col:
            st.error(
                f"Не удалось найти нужные столбцы. Доступные столбцы в файле: {list(df.columns)}"
            )
            return None

        # Переименовываем их для стабильной работы
        df = df.rename(columns={sum_col[0]: "Сумма", addr_col[0]: "Адрес"})

        # Очищаем и преобразуем Сумму в числа
        df["Сумма"] = df["Сумма"].astype(str).str.replace(r"[^\d.]", "", regex=True)
        df["Сумма"] = pd.to_numeric(df["Сумma"], errors="coerce").fillna(0)

        return df
    except Exception as e:
        st.error(f"Ошибка при разборе файла: {e}")
        return None


df = load_data(DATA_URL)

if df is not None:
    total_revenue = df["Сумма"].sum()
    total_transactions = len(df)
    unique_salons = df["Адрес"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Общая выручка", f"{total_revenue:,.0f} ₽".replace(",", " "))
    col2.metric("Количество услуг", f"{total_transactions}")
    col3.metric("Активных точек", f"{unique_salons}")

    st.markdown("---")

    # Группировка
    df_grouped = df.groupby("Адрес")["Сумма"].sum().reset_index()

    # Диаграмма
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

    chart_col, table_col = st.columns()

    with chart_col:
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        st.subheader("Выручка детально")
        df_table = df_grouped.copy()
        df_table["Сумма"] = df_table["Сумма"].map("{:,.0f} ₽".format)
        st.dataframe(df_table, use_container_width=True, hide_index=True)
