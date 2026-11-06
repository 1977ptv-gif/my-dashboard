import pandas as pd
import plotly.express as px
import streamlit as st

# Настройка страницы дашборда
st.set_page_config(
    page_title="Салон РИО — Аналитика", page_icon="✂️", layout="wide"
)

st.title("📊 Интерактивный дашборд сети салонов «РИО»")
st.markdown("---")

# Прямая ссылка на ваш CSV-файл (замените на вашу ссылку, если файл лежит в другом месте)
# Для примера код настроен на чтение файла, лежащего в том же репозитории GitHub
DATA_URL = "data.csv"


@st.cache_data
def load_data(url):
    try:
        # Читаем данные, принудительно обрабатывая кавычки и запятые
        df = pd.read_csv(url, sep=",", quotechar='"')
        # Очищаем названия столбцов от лишних пробелов
        df.columns = df.columns.str.strip()
        # Преобразуем столбец Сумма в числовой формат
        df["Сумма"] = pd.to_numeric(df["Сумма"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")
        return None


# Загрузка датасета
df = load_data(DATA_URL)

if df is not None:
    # 1. Считаем общие метрики для верхней панели
    total_revenue = df["Сумма"].sum()
    total_transactions = len(df)
    unique_salons = df["Адрес салона"].nunique()

    # Отображение ключевых показателей
    col1, col2, col3 = st.columns(3)
    col1.metric("Общая выручка", f"{total_revenue:,.0f} ₽".replace(",", " "))
    col2.metric("Количество услуг", f"{total_transactions}")
    col3.metric("Активных точек", f"{unique_salons}")

    st.markdown("---")

    # 2. Подготовка данных для круговой диаграммы (группировка Суммы по Адресу салона)
    df_grouped = (
        df.groupby("Адрес салона")["Сумма"].sum().reset_index()
    )

    # 3. Построение диаграммы с помощью Plotly
    fig = px.pie(
        df_grouped,
        values="Сумма",
        names="Адрес салона",
        title="Доля выручки по адресам салонов",
        hole=0.4,  # Делает диаграмму в виде бублика (donut chart) для красоты
        color_discrete_sequence=px.colors.sequential.RdBu,
    )

    # Настройка подписей на графике
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Выручка: %{value:,.0f} ₽<extra></percent></extra>",
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
        ),
    )

    # Вывод графика и таблицы данных рядом
    chart_col, table_col = st.columns([2, 1])

    with chart_col:
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        st.subheader("Выручка детально")
        # Красивое форматирование таблицы перед выводом
        df_table = df_grouped.copy()
        df_table["Сумма"] = df_table["Сумма"].map("{:,.0f} ₽".format)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

else:
    st.info("Пожалуйста, проверьте правильность размещения файла data.csv.")
