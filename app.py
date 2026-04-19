import streamlit as st
import holidays
import calendar
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="AI Release Planning Agent", page_icon="🚀", layout="centered")

st.title("AI Release Planning Agent 🚀")

# ===== Inputs =====
developers = st.number_input("Number of Developers", value=1, min_value=1)
testers = st.number_input("Number of QA / Testers", value=1, min_value=0)
start_date = st.date_input("Project Start Date", value=date.today())

st.subheader("Timeline")
col1, col2 = st.columns(2)

with col1:
    months = st.number_input("Months", value=5, min_value=0)

with col2:
    extra_days = st.number_input("Days", value=0, min_value=0)

vacation_days = st.number_input("Vacation Days Per Employee", value=10, min_value=0)
focus_factor = st.slider("Focus Factor", min_value=0.1, max_value=1.0, value=0.8, step=0.05)


# ===== Functions =====
def get_israeli_holidays(years):
    holiday_dict = {}
    for year in years:
        holiday_dict.update(holidays.CountryHoliday("IL", years=year))
    return holiday_dict


def add_months_and_days(start_date, months, extra_days):
    month = start_date.month - 1 + months
    year = start_date.year + month // 12
    month = month % 12 + 1

    day = min(start_date.day, calendar.monthrange(year, month)[1])
    end_date = date(year, month, day) + timedelta(days=extra_days)

    return end_date


def calculate_working_days(start_date, months, extra_days):
    end_date = add_months_and_days(start_date, months, extra_days)
    years = list(range(start_date.year, end_date.year + 1))
    israeli_holidays = get_israeli_holidays(years)

    working_days = 0
    current_day = start_date

    while current_day < end_date:
        if current_day.weekday() in [6, 0, 1, 2, 3]:  # Sunday-Thursday
            if current_day not in israeli_holidays:
                working_days += 1
        current_day += timedelta(days=1)

    return working_days, end_date


def calculate_days_per_month(start_date, months, extra_days):
    working_days, _ = calculate_working_days(start_date, months, extra_days)
    total_project_months = months + (extra_days / 30)

    if total_project_months > 0:
        days_per_month = working_days / total_project_months
    else:
        days_per_month = 0

    return days_per_month, working_days


def calculate_team_capacity(headcount, start_date, months, extra_days, vacation_days, focus_factor):
    working_days, end_date = calculate_working_days(start_date, months, extra_days)
    days_per_month, _ = calculate_days_per_month(start_date, months, extra_days)

    effective_days = max(working_days - vacation_days, 0)
    capacity_days = headcount * effective_days * focus_factor

    if days_per_month > 0:
        capacity_months = capacity_days / days_per_month
    else:
        capacity_months = 0

    return capacity_months, end_date, working_days, effective_days, days_per_month


def format_gap_status(days_value):
    """Return readable shortage/surplus text for days."""
    if days_value >= 0:
        return f"{abs(days_value):.1f} days surplus"
    return f"{abs(days_value):.1f} days shortage"


# ===== Capacity Preview =====
if st.button("Calculate Capacity"):
    dev_capacity, end_date, dev_working_days, dev_effective_days, days_per_month = calculate_team_capacity(
        developers, start_date, months, extra_days, vacation_days, focus_factor
    )

    qa_capacity, _, qa_working_days, qa_effective_days, _ = calculate_team_capacity(
        testers, start_date, months, extra_days, vacation_days, focus_factor
    )

    st.subheader("Results")
    st.write(f"Project End Date: {end_date}")
    st.write(f"Actual Working Days Per Month: {days_per_month:.2f}")

    st.markdown("### Developers")
    st.write(f"Working Days per Developer: {dev_working_days}")
    st.write(f"Effective Working Days per Developer: {dev_effective_days}")
    st.write(f"Total Developer Capacity: {dev_capacity:.2f} man-months")

    st.markdown("### QA / Testers")
    st.write(f"Working Days per Tester: {qa_working_days}")
    st.write(f"Effective Working Days per Tester: {qa_effective_days}")
    st.write(f"Total QA Capacity: {qa_capacity:.2f} man-months")


# ===== Features & Streams =====
st.header("Project Scope")

num_features = st.number_input("Number of Features", min_value=1, value=3, step=1)

features_data = []
total_dev_effort_days = 0
total_qa_effort_days = 0

for i in range(int(num_features)):
    feature_name = st.text_input(
        f"Feature Name {i+1}",
        value=f"Feature {i+1}",
        key=f"feature_name_{i}"
    )

    st.subheader(f"🚀 {feature_name}")

    business_value = st.slider(
        f"Business Value - {feature_name}",
        min_value=1,
        max_value=10,
        value=5,
        key=f"business_value_{i}",
        help="Rate the business importance of this feature from 1 (low) to 10 (high)."
    )

    num_streams = st.number_input(
        f"Number of Streams for {feature_name}",
        min_value=1,
        value=1,
        step=1,
        key=f"num_streams_{i}"
    )

    streams_data = []
    feature_dev_effort_days = 0
    feature_qa_effort_days = 0

    for j in range(int(num_streams)):
        stream_name = st.text_input(
            f"Stream Name - {feature_name}, Stream {j+1}",
            value=f"Stream {j+1}",
            key=f"stream_name_{i}_{j}"
        )

        st.markdown(f"#### 🔹 {stream_name}")

        col1, col2 = st.columns(2)
        with col1:
            developers_needed = st.number_input(
                f"Developers Needed - {stream_name}",
                min_value=0,
                value=1,
                step=1,
                key=f"dev_needed_{i}_{j}"
            )
        with col2:
            testers_needed = st.number_input(
                f"QA Needed - {stream_name}",
                min_value=0,
                value=1,
                step=1,
                key=f"qa_needed_{i}_{j}"
            )

        col3, col4 = st.columns(2)
        with col3:
            dev_days = st.number_input(
                f"Development Days - {stream_name}",
                min_value=0.0,
                value=10.0,
                step=1.0,
                key=f"dev_days_{i}_{j}"
            )
        with col4:
            qa_days = st.number_input(
                f"QA Days - {stream_name}",
                min_value=0.0,
                value=5.0,
                step=1.0,
                key=f"qa_days_{i}_{j}"
            )

        stream_dev_effort = developers_needed * dev_days
        stream_qa_effort = testers_needed * qa_days

        feature_dev_effort_days += stream_dev_effort
        feature_qa_effort_days += stream_qa_effort

        streams_data.append({
            "stream_name": stream_name,
            "developers_needed": developers_needed,
            "testers_needed": testers_needed,
            "dev_days": dev_days,
            "qa_days": qa_days,
            "stream_dev_effort": stream_dev_effort,
            "stream_qa_effort": stream_qa_effort
        })

    total_dev_effort_days += feature_dev_effort_days
    total_qa_effort_days += feature_qa_effort_days

    feature_total_effort_days = feature_dev_effort_days + feature_qa_effort_days
    priority_score = business_value / feature_total_effort_days if feature_total_effort_days > 0 else 0

    features_data.append({
        "feature_name": feature_name,
        "business_value": business_value,
        "num_streams": num_streams,
        "streams": streams_data,
        "feature_dev_effort_days": feature_dev_effort_days,
        "feature_qa_effort_days": feature_qa_effort_days,
        "feature_total_effort_days": feature_total_effort_days,
        "priority_score": priority_score
    })

    st.info(
        f"Feature Summary – {feature_name} | "
        f"Business Value: {business_value} | "
        f"Dev Effort: {feature_dev_effort_days:.1f} person-days | "
        f"QA Effort: {feature_qa_effort_days:.1f} person-days | "
        f"Total Effort: {feature_total_effort_days:.1f} person-days | "
        f"Priority Score: {priority_score:.3f}"
    )


# ===== Project Totals =====
st.subheader("Project Totals")

st.write(f"Total Development Effort: {total_dev_effort_days:.1f} person-days")
st.write(f"Total QA Effort: {total_qa_effort_days:.1f} person-days")

days_per_month, project_working_days = calculate_days_per_month(start_date, months, extra_days)

total_dev_effort_months = total_dev_effort_days / days_per_month if days_per_month > 0 else 0
total_qa_effort_months = total_qa_effort_days / days_per_month if days_per_month > 0 else 0

st.write(f"Total Development Effort: {total_dev_effort_months:.2f} man-months")
st.write(f"Total QA Effort: {total_qa_effort_months:.2f} man-months")


# ===== Final Analysis =====
if st.button("Analyze Project Capacity"):
    dev_capacity, end_date, dev_working_days, dev_effective_days, days_per_month = calculate_team_capacity(
        developers, start_date, months, extra_days, vacation_days, focus_factor
    )

    qa_capacity, _, qa_working_days, qa_effective_days, _ = calculate_team_capacity(
        testers, start_date, months, extra_days, vacation_days, focus_factor
    )

    dev_gap = dev_capacity - total_dev_effort_months
    qa_gap = qa_capacity - total_qa_effort_months

    dev_gap_days = abs(dev_gap) * days_per_month
    qa_gap_days = abs(qa_gap) * days_per_month

    st.header("Capacity Analysis")

    st.subheader("Developers")
    st.write(f"Available Developer Capacity: {dev_capacity:.2f} man-months")
    st.write(f"Required Development Effort: {total_dev_effort_months:.2f} man-months")
    st.write(f"Developer Gap: {dev_gap:.2f} man-months")

    if dev_gap >= 0:
        st.success(f"Developer Capacity Status: Over Capacity by {dev_gap_days:.1f} working days")
    else:
        st.error(f"Developer Capacity Status: Under Capacity by {dev_gap_days:.1f} working days")

    st.subheader("QA / Testers")
    st.write(f"Available QA Capacity: {qa_capacity:.2f} man-months")
    st.write(f"Required QA Effort: {total_qa_effort_months:.2f} man-months")
    st.write(f"QA Gap: {qa_gap:.2f} man-months")

    if qa_gap >= 0:
        st.success(f"QA Capacity Status: Over Capacity by {qa_gap_days:.1f} working days")
    else:
        st.error(f"QA Capacity Status: Under Capacity by {qa_gap_days:.1f} working days")

    st.subheader("Project Overview")
    st.write(f"Project End Date: {end_date}")

    if dev_gap >= 0 and qa_gap >= 0:
        st.success("The project scope is feasible within the current timeline and team capacity.")
    else:
        st.warning("The project scope is not fully aligned with the current timeline and team capacity.")

    # ===== Relative Prioritization =====
    st.header("Feature Prioritization Table")

    sorted_features = sorted(
        features_data,
        key=lambda x: x["priority_score"],
        reverse=True
    )

    total_features = len(sorted_features)
    high_cutoff = max(1, round(total_features * 0.3))
    medium_cutoff = max(1, round(total_features * 0.7))

    table_data = []

    for idx, feature in enumerate(sorted_features, start=1):
        if idx <= high_cutoff:
            priority = "High"
        elif idx <= medium_cutoff:
            priority = "Medium"
        else:
            priority = "Low"

        feature["suggested_priority"] = priority

        table_data.append({
            "Rank": idx,
            "Feature": feature["feature_name"],
            "Business Value": feature["business_value"],
            "Dev Effort (days)": round(feature["feature_dev_effort_days"], 1),
            "QA Effort (days)": round(feature["feature_qa_effort_days"], 1),
            "Total Effort (days)": round(feature["feature_total_effort_days"], 1),
            "Priority Score": round(feature["priority_score"], 3),
            "Priority": priority
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.success(f"Top Priority Feature: {df.iloc[0]['Feature']}")

    # ===== Scope Adjustment Preview =====
    if dev_gap < 0 or qa_gap < 0:
        st.subheader("Recommended Scope Adjustment")
        st.write("To improve feasibility, consider postponing these features first:")

        lowest_priority_features = sorted(
            features_data,
            key=lambda x: x["priority_score"]
        )

        for feature in lowest_priority_features[:3]:
            st.write(
                f"- {feature['feature_name']} "
                f"(Priority Score: {feature['priority_score']:.3f}, "
                f"Business Value: {feature['business_value']}, "
                f"Total Effort: {feature['feature_total_effort_days']:.1f} person-days, "
                f"Priority: {feature.get('suggested_priority', 'N/A')})"
            )
    else:
        st.subheader("Recommended Next Step")
        st.write("The current scope fits the available capacity. You can keep all features in the release and execute by priority order.")

    # ===== Recommendations =====
    st.header("Recommendations")

    dev_surplus_days = max(dev_gap, 0) * days_per_month
    qa_surplus_days = max(qa_gap, 0) * days_per_month
    dev_shortage_days = abs(min(dev_gap, 0)) * days_per_month
    qa_shortage_days = abs(min(qa_gap, 0)) * days_per_month

    high_priority_features = [f for f in sorted_features if f.get("suggested_priority") == "High"]
    medium_priority_features = [f for f in sorted_features if f.get("suggested_priority") == "Medium"]
    low_priority_features = [f for f in sorted_features if f.get("suggested_priority") == "Low"]

    if dev_gap >= 0 and qa_gap >= 0:
        st.success("The project currently has extra capacity. Recommended actions:")

        st.write("- Keep part of the extra capacity as a delivery buffer for risks, delays, and unexpected issues.")

        if high_priority_features:
            st.write("- Expand scope for high-priority features before adding low-value work.")
            for feature in high_priority_features[:3]:
                st.write(
                    f"  • Consider expanding '{feature['feature_name']}' "
                    f"(Priority Score: {feature['priority_score']:.3f}, Business Value: {feature['business_value']})"
                )

        if medium_priority_features:
            st.write("- If buffer remains, consider pulling medium-priority features into the release:")
            for feature in medium_priority_features[:3]:
                st.write(
                    f"  • '{feature['feature_name']}' "
                    f"(Priority Score: {feature['priority_score']:.3f}, Total Effort: {feature['feature_total_effort_days']:.1f} days)"
                )

        if qa_surplus_days > 0:
            st.write(
                f"- QA has {qa_surplus_days:.1f} extra days available. "
                f"Use them to increase regression coverage, test edge cases, and improve release quality."
            )

        if dev_surplus_days > 0:
            st.write(
                f"- Developers have {dev_surplus_days:.1f} extra days available. "
                f"Use them for code cleanup, stability improvements, internal tooling, or technical debt reduction."
            )

        if low_priority_features and high_priority_features:
            st.write("- Reallocate effort from low-priority work toward higher-priority features if needed.")
            for low_feature in low_priority_features[:2]:
                st.write(
                    f"  • '{low_feature['feature_name']}' is lower priority and may be deferred or reduced "
                    f"to free capacity for more valuable work."
                )

    elif dev_gap >= 0 and qa_gap < 0:
        st.warning("Developers have extra capacity, but QA is still a bottleneck.")

        qa_support_factor = 0.5
        qa_help_from_dev = dev_surplus_days * qa_support_factor
        remaining_qa_shortage = max(qa_shortage_days - qa_help_from_dev, 0)

        st.write(f"- Developers have {dev_surplus_days:.1f} extra days available.")
        st.write(
            f"- With a QA support efficiency of {qa_support_factor:.0%}, "
            f"developer surplus can contribute about {qa_help_from_dev:.1f} QA-effective days."
        )

        if remaining_qa_shortage == 0:
            st.success("- Developer support can fully cover the QA bottleneck.")
        else:
            st.warning(
                f"- Developer support can reduce the QA bottleneck, but about {remaining_qa_shortage:.1f} QA days will still remain uncovered."
            )

        st.write("- Focus developers on QA-supporting tasks such as regression execution, bug reproduction, and flow validation.")
        st.write("- Reduce QA scope strategically by focusing on critical flows and high-risk areas first.")
        st.write("- Consider an MVP release if QA coverage cannot fully support the full scope.")

    elif dev_gap < 0 and qa_gap >= 0:
        st.warning("Development is the bottleneck, while QA still has available capacity.")

        st.write(f"- Development is missing approximately {dev_shortage_days:.1f} working days.")
        st.write(f"- QA has approximately {qa_surplus_days:.1f} extra days available.")

        st.write("- QA cannot remove the development bottleneck, but can prepare ahead by writing test cases, test scenarios, and regression plans.")
        st.write("- Convert medium and low-priority features into MVP scope to reduce development effort.")
        st.write("- Reduce or defer lower-priority technical work that does not affect release value.")
        st.write("- If needed, postpone lower-priority features until the development gap is closed.")

    elif dev_gap < 0 and qa_gap < 0:
        st.warning("Both Development and QA are under capacity. Scope reduction is required.")

        st.write(f"- Developers are missing approximately {dev_shortage_days:.1f} working days.")
        st.write(f"- QA is missing approximately {qa_shortage_days:.1f} working days.")

        st.subheader("Suggested Scope Reduction")

        sorted_low_to_high = sorted(features_data, key=lambda x: x["priority_score"])
        removed_features = []
        accumulated_dev = 0
        accumulated_qa = 0

        for feature in sorted_low_to_high:
            if accumulated_dev >= dev_shortage_days and accumulated_qa >= qa_shortage_days:
                break

            removed_features.append(feature)
            accumulated_dev += feature["feature_dev_effort_days"]
            accumulated_qa += feature["feature_qa_effort_days"]

        for f in removed_features:
            st.write(
                f"• Remove or defer '{f['feature_name']}' "
                f"(Dev: {f['feature_dev_effort_days']:.1f} days, "
                f"QA: {f['feature_qa_effort_days']:.1f} days, "
                f"Priority Score: {f['priority_score']:.3f})"
            )

        new_dev_balance_after_bundle = accumulated_dev - dev_shortage_days
        new_qa_balance_after_bundle = accumulated_qa - qa_shortage_days

        st.info(
            f"These changes would free approximately {accumulated_dev:.1f} development days "
            f"and {accumulated_qa:.1f} QA days."
        )

        st.info(
            f"After removing these features: "
            f"Dev = {format_gap_status(new_dev_balance_after_bundle)}, "
            f"QA = {format_gap_status(new_qa_balance_after_bundle)}"
        )

        st.write("- Create MVP versions for large features instead of delivering full scope.")
        st.write("- Reduce QA scope carefully by focusing on critical user journeys and high-risk validations.")
        st.write("- Consider adding temporary resources or extending the timeline if scope cannot move.")

        # ===== Impact of Removing Individual Features =====
        st.subheader("Impact of Removing Individual Features")

        individual_impact_rows = []

        for feature in sorted_low_to_high:
            dev_days_saved = feature["feature_dev_effort_days"]
            qa_days_saved = feature["feature_qa_effort_days"]

            # Negative gap means shortage, so adding saved days reduces shortage
            new_dev_balance = dev_days_saved - dev_shortage_days
            new_qa_balance = qa_days_saved - qa_shortage_days

            individual_impact_rows.append({
                "Feature": feature["feature_name"],
                "Priority Score": round(feature["priority_score"], 3),
                "Priority": feature.get("suggested_priority", "N/A"),
                "Dev Days Saved": round(dev_days_saved, 1),
                "QA Days Saved": round(qa_days_saved, 1),
                "Dev After Removal": format_gap_status(new_dev_balance),
                "QA After Removal": format_gap_status(new_qa_balance)
            })

        impact_df = pd.DataFrame(individual_impact_rows)
        st.dataframe(impact_df, use_container_width=True)

        st.write("This table shows exactly how much shortage or surplus would remain after removing each feature individually.")
        