import streamlit as st
from fpdf import FPDF
import json
import requests
import re

# Function to calculate proficiency bonus
def calculate_proficiency_bonus(level):
    if level <= 4:
        return 2
    elif level <= 8:
        return 3
    elif level <= 12:
        return 4
    elif level <= 16:
        return 5
    else:
        return 6

# Function to calculate ability modifier
def calculate_modifier(score):
    return (score - 10) // 2

# Function to generate PDF
def generate_pdf(character):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Set Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "D&D 5e Character Sheet", ln=True, align='C')
    pdf.ln(10)

    # Character Information
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Race: {character['Race']}", ln=True)
    pdf.cell(0, 10, f"Class: {character['Class']}", ln=True)
    pdf.cell(0, 10, f"Level: {character['Level']}", ln=True)
    pdf.cell(0, 10, f"Proficiency Bonus: +{character['Proficiency Bonus']}", ln=True)

    # Ability Scores
    pdf.cell(0, 10, "Ability Scores:", ln=True)
    for ability, score in character['Ability Scores'].items():
        pdf.cell(0, 10, f"{ability}: {score}", ln=True)

    # Skills
    pdf.cell(0, 10, "Skills:", ln=True)
    for skill, modifier in character['Skills'].items():
        pdf.cell(0, 10, f"{skill}: {modifier:+}", ln=True)

    # HP and AC
    pdf.cell(0, 10, f"Hit Points: {character['HP']}", ln=True)
    pdf.cell(0, 10, f"Armor Class: {character['AC']}", ln=True)

    # Weapons
    pdf.cell(0, 10, "Weapons:", ln=True)
    for weapon in character['Weapons']:
        if weapon:
            pdf.cell(0, 10, f"- {weapon}", ln=True)

    # Armor
    pdf.cell(0, 10, "Armors:", ln=True)
    for armor in character['Armors']:
        if armor:
            pdf.cell(0, 10, f"- {armor}", ln=True)

    # Spells
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Spells", ln=True)
    pdf.set_font("Arial", '', 12)
    for level, spells in character['Spells'].items():
        active_spells = [spell for spell in spells if spell]
        if active_spells:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Spell Level {level}:", ln=True)
            pdf.set_font("Arial", '', 12)
            for spell in active_spells:
                pdf.cell(10, 10, "-", ln=False)
                pdf.cell(0, 10, f" {spell}", ln=True)
    pdf.ln(5)

    return bytes(pdf.output(dest='S'))  # Return PDF as bytes

# Main function
def main():
    st.set_page_config(page_title="D&D 5e Character Sheet", layout="wide")
    st.title("🧙‍♂️ D&D 5e Character Sheet")

    # --------------------- Character Information ---------------------
    st.header("📝 Character Information")
    race = st.text_input("**Race**", value="Human")
    lass = st.text_input("**Class**", value="Sorceror")
    level = st.number_input("**Level**", min_value=1, max_value=20, value=1, step=1)
    proficiency_bonus = calculate_proficiency_bonus(level)
    st.markdown(f"**Proficiency Bonus:** `+{proficiency_bonus}`")

    # --------------------- Ability Scores & Skills ---------------------
    st.header("📊 Ability Scores & 🎯 Skills")
    abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

    # Define skills by their corresponding abilities
    skills_dict = {
        "Strength": ["Athletics"],
        "Dexterity": ["Acrobatics", "Sleight of Hand", "Stealth"],
        "Intelligence": ["Arcana", "History", "Investigation", "Nature", "Religion"],
        "Wisdom": ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"],
        "Charisma": ["Deception", "Intimidation", "Performance", "Persuasion"]
    }

    # Initialize dictionaries to store ability scores, modifiers, and skills
    ability_scores = {}
    ability_mods = {}
    skills_final = {}

    # Arrange abilities in three columns
    ability_cols = st.columns(3)
    for idx, ability in enumerate(abilities):
        with ability_cols[idx % 3]:
            st.subheader(f"**{ability}**")
            score = st.number_input(
                f"{ability} Score",
                min_value=1,
                max_value=30,
                value=10,
                step=1,
                key=f"{ability}_score"
            )
            modifier = calculate_modifier(score)
            st.markdown(f"*Modifier:* `{modifier:+}`")
            ability_scores[ability] = score
            ability_mods[ability] = modifier

            # List associated skills
            if ability in skills_dict:
                for skill in skills_dict[ability]:
                    st.markdown(f"**{skill}**")
                    # Create two checkboxes for proficiency
                    proficiency1 = st.checkbox(
                        f"Proficiency in {skill} (Add +{proficiency_bonus})",
                        key=f"{skill}_prof1"
                    )
                    proficiency2 = st.checkbox(
                        f"Expertise in {skill} (Add +{proficiency_bonus} again)",
                        key=f"{skill}_prof2"
                    )
                    # Calculate total proficiency
                    total_proficiency = 0
                    if proficiency1:
                        total_proficiency += proficiency_bonus
                    if proficiency2:
                        total_proficiency += proficiency_bonus
                    # Final skill value
                    final_skill = modifier + total_proficiency
                    skills_final[skill] = final_skill
                    st.markdown(f"**Final {skill} Modifier:** `{final_skill:+}`")
                    st.markdown("---")  # Separator for clarity

    # --------------------- Health and Armor ---------------------
    st.header("❤️ Health and Armor")
    hp = st.number_input("**Hit Points (HP)**", min_value=1, value=10, step=1)
    ac = st.number_input("**Armor Class (AC)**", min_value=1, value=10, step=1)

    # --------------------- Equipment ---------------------
    st.header("🎒 Equipment")
    # Weapons
    st.subheader("🗡️ Weapons")
    weapons = []
    for i in range(1, 4):
        weapon = st.text_input(f"**Weapon {i}**", key=f"weapon_{i}")
        weapons.append(weapon)
    # Armor
    st.subheader("🛡️ Armor")
    armors = []
    for i in range(1, 4):
        armor = st.text_input(f"**Armor {i}**", key=f"armor_{i}")
        armors.append(armor)

    # --------------------- Spell Spaces ---------------------
    st.header("✨ Spells")
    spell_levels = list(range(0, 10))
    spells = {}

    for level_num in spell_levels:
        with st.expander(f"📖 Spell Level {level_num}"):
            spells[level_num] = []
            for i in range(1, 7):
                spell = st.text_input(
                    f"**Spell {i}**",
                    key=f"spell_{level_num}_{i}"
                )
                spells[level_num].append(spell)

    # --------------------- Display Summary ---------------------
    if st.button("📄 Show Summary"):
        st.markdown("---")
        st.subheader("📜 **Character Summary**")

        # Character Information
        st.markdown("### 📝 Character Information")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Race:** {race}")
            st.write(f"**Class:** {lass}")
        with col2:
            st.write(f"**Level:** {level}")
            st.write(f"**Proficiency Bonus:** `+{proficiency_bonus}`")

        # Ability Scores and Modifiers
        st.markdown("### 📊 Ability Scores and Modifiers")
        ability_table = []
        for ability in abilities:
            ability_table.append({
                "Ability": ability,
                "Score": ability_scores[ability],
                "Modifier": f"{ability_mods[ability]:+}"
            })
        st.table(ability_table)

        # Skills
        st.markdown("### 🎯 Skills")
        skills_table = []
        for ability, skill_list in skills_dict.items():
            for skill in skill_list:
                skills_table.append({
                    "Skill": skill,
                    "Final Modifier": f"{skills_final[skill]:+}"
                })
        st.table(skills_table)

        # Health and Armor
        st.markdown("### ❤️ Health and Armor")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Hit Points (HP):** {hp}")
        with col2:
            st.write(f"**Armor Class (AC):** {ac}")

        # Equipment
        st.markdown("### 🎒 Equipment")
        # Weapons
        st.subheader("🗡️ Weapons")
        for weapon in weapons:
            if weapon:
                st.write(f"- {weapon}")
        # Armor
        st.subheader("🛡️ Armor")
        for armor in armors:
            if armor:
                st.write(f"- {armor}")

        # Spells
        st.markdown("### ✨ Spells")
        for level_num in spell_levels:
            active_spells = [spell for spell in spells[level_num] if spell]
            if active_spells:
                st.markdown(f"**📖 Spell Level {level_num}:**")
                for spell in active_spells:
                    st.write(f"- {spell}")

    # --------------------- Download Character Sheet as PDF ---------------------
    st.header("📥 Download Character Sheet as PDF")
    if st.button("Download"):
        character = {
            "Race": race,
            "Class": lass,
            "Level": level,
            "Proficiency Bonus": proficiency_bonus,
            "Ability Scores": ability_scores,
            "Skills": skills_final,
            "HP": hp,
            "AC": ac,
            "Weapons": weapons,
            "Armors": armors,
            "Spells": spells
        }

        # Generate PDF
        pdf_bytes = generate_pdf(character)

        # Create a download button for the PDF
        st.download_button(
            label="📄 Download as PDF",
            data=pdf_bytes,
            file_name="dnd_character_sheet.pdf",
            mime="application/pdf"
        )

    # --------------------- Spell Search ---------------------
    st.header("🔍 Spell Search")
    
    spells_name = st.text_input("Enter the spell name:")
    goButton_spells = st.button("Search Spell")

    if goButton_spells:
        input_name = spells_name.strip()
        if input_name:
            formatted_name = input_name.replace(" ", "-")
            generated_link = f"https://www.aidedd.org/dnd/sorts.php?vo={formatted_name}"
            
            try:
                response = requests.get(generated_link)
                if response.status_code == 200:
                    content = response.text
                
                    # Remove all <script> tags and their contents
                    content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
                
                    # Remove specific JavaScript lines like 'window.dataLayer' or 'gtag'
                    content = re.sub(r'window\.dataLayer\s*=\s*\[\];', '', content)
                    content = re.sub(r'gtag\(.*?\);', '', content)
                
                    # Further clean the HTML by removing any other tags
                    cleaned_content = re.sub(r'<.*?>', '', content)
                    
                    # Find the position of the spell name
                    pattern = re.compile(re.escape(input_name), re.IGNORECASE)
                    match = pattern.search(cleaned_content)
                    if match:
                        spell_position = match.start()
                        cleaned_content = cleaned_content[spell_position:]
                    else:
                        st.warning("Spell name not found in the content.")
                    
                    st.text_area("Spell Details", cleaned_content, height=300)
                else:
                    st.error("Failed to fetch the webpage.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a spell name.")
    
    st.markdown("""
    ### Spells Resources:
    - [Spells Filter](https://www.aidedd.org/dnd-filters/spells-5e.php)
    """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()