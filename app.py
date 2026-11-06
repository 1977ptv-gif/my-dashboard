import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Салон РИО — Аналитика", page_icon="✂️", layout="wide"
)

st.title("📊 Интерактивный дашборд сети салонов «РИО»")
st.markdown("---")

# ВСТАВЬТЕ СЮДА ВАШУ СКОПИРОВАННУЮ ССЫЛКУ ИЗ GOOGLE ТАБЛИЦЫ:
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXZQQTF_gApySv_y2ZNVuAGo_8RmH_5zQ33mhXDF_SXUXGC49lp-1DlU-JKrx0uXhnqiwPoCnONA6i/pub?output=csv"


@st.cache_data(ttl=60)  # Данные будут обновляться каждые 60 секунд при обновлении страницы
def load_data(url):
    try:
        # Читаем данные из Google Таблицы (разделитель - обычная запятая)
        df = pd.read_csv(url, sep=",", on_bad_lines="skip")

        # Очищаем названия столбцов
        df.columns = df.columns.str.strip().str.replace('"', "")

        # Точные имена столбцов из вашей таблицы
        addr_col = "название салона"
        sum_col = "Сумма"
        master_col = "Мастер"

        if sum_col not in df.columns or addr_col not in df.columns:
            st.error(
                f"Ошибка структуры! Доступные столбцы: {list(df.columns)}"
            )
            return None

        df = df.rename(columns={sum_col: "Сумма", addr_col: "Адрес"})
        if master_col in df.columns:
            df = df.rename(columns={master_col: "Мастер"})

        # Очищаем суммы и переводим в числа
        df["Сумма"] = df["Сумма"].astype(str).str.replace(r"[^\d.]", "", regex=True)
        df["Сумма"] = pd.to_numeric(df["Сумма"], errors="coerce").fillna(0)

        return df
    except Exception as e:
        st.error(f"Ошибка при разборе файла: {e}")
        return None


df = load_data(DATA_URL)

if df is not None:
    # Список салонов для фильтра
    salon_options = ["Все салоны"] + sorted(df["Адрес"].unique().tolist())
    selected_salon = st.selectbox("📍 Выберите салон для фильтрации данных:", salon_options)

    if selected_salon == "Все салоны":
        df_filtered = df.copy()
    else:
        df_filtered = df[df["Адрес"] == selected_salon]

    st.markdown("---")

    # Основные метрики
    total_revenue = df_filtered["Сумма"].sum()
    total_transactions = len(df_filtered)
    unique_salons = df_filtered["Адрес"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Выручка", f"{total_revenue:,.0f} ₽".replace(",", " "))
    col2.metric("Количество услуг", f"{total_transactions}")
    col3.metric("Активных точек в фильтре", f"{unique_salons}")

    st.markdown("---")

    # Круговая диаграмма
    df_grouped = df_filtered.groupby("Адрес")["Сумма"].sum().reset_index()
    df_grouped = df_grouped.sort_values(by="Сумма", ascending=False)

    fig_pie = px.pie(
        df_grouped,
        values="Сумма",
        names="Адрес",
        title="Доля выручки по адресам салонов",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_pie.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Выручка: %{value:,.0f} ₽<extra></extra>",
    )

    chart_col, table_col = st.columns(2)
    with chart_col:
        st.plotly_chart(fig_pie, use_container_width=True)
    with table_col:
        st.subheader("Выручка детально")
        df_table = df_grouped.copy()
        df_table["Сумма"] = df_table["Сумма"].map("{:,.0f} ₽".format)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

    # Рейтинг мастеров
    if "Мастер" in df_filtered.columns:
        st.markdown("---")
        st.subheader(f"🏆 Рейтинг востребованности мастеров (Топ-10) — {selected_salon}")

        df_masters = df_filtered["Мастер"].value_counts().reset_index(name="Количество").head(10)
        df_masters = df_masters.sort_values(by="Количество", ascending=True)

        if not df_masters.empty:
            fig_bar = px.bar(
                df_masters,
                x="Количество",
                y="Мастер",
                orientation="h",
                labels={"Количество": "Выполнено услуг (шт.)", "Мастер": "Имя мастера"},
                color="Количество",
                color_continuous_scale=px.colors.sequential.Viridis,
            )
            fig_bar.update_layout(showlegend=False, margin=dict(l=150, r=20, t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)
