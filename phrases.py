                for child in view.children:
                    child.disabled = True
                    if child.custom_id == f"opt_{correct_idx}":
                        child.style = discord.ButtonStyle.success
                    elif child.label == chosen_label and not correct:
                        child.style = discord.ButtonStyle.danger

                if correct:
                    u = await load_user_data(inter.user.id)
                    u["quiz_coins"] = u.get("quiz_coins", 0) + 10
                    u["quiz_level"] = min(u.get("quiz_level", 0) + 1, 9)
                    await save_user_data(inter.user.id, u)
                    await inter.response.edit_message(
                        content=f"✅ صح! **{chosen_label}** هي الصح. +10 عملات",
                        embed=None,
                        view=view
                    )
                else:
                    await inter.response.edit_message(
                        content=f"❌ غلط! الصح هو **{q['options'][correct_idx]}**",
                        embed=None,
                        view=view
                    )
