import pytest
import sys
import os
import random
from unittest.mock import patch, MagicMock
from src.playground.analyze_and_refactor_system_implementeer_selfimprovement_squad import SelfImprovementSquad
import time
from loguru import logger

sys.path.append(os.getcwd())


class TestSelfImprovementSquad:
    @pytest.fixture
    def squad(self):
        return SelfImprovementSquad("TestSquad", 2)

    def test_init(self, squad):
        assert squad.squad_name == "TestSquad"
        assert squad.members == 2
        assert len(squad.member_skills) == 2
        for member, skills in squad.member_skills.items():
            assert "coding" in skills
            assert "debugging" in skills
            assert "testing" in skills
            assert 1 <= skills["coding"] <= 5
            assert 1 <= skills["debugging"] <= 5
            assert 1 <= skills["testing"] <= 5

    @patch.object(logger, 'info')
    def test_initialize_members(self, mock_logger_info, squad):
        squad._initialize_members()
        assert mock_logger_info.called
        assert mock_logger_info.call_count == 1
        assert "Initialized squad" in str(mock_logger_info.call_args)


    @patch.object(logger, 'info')
    def test_display_member_skills(self, mock_logger_info, squad):
        squad.display_member_skills()
        assert mock_logger_info.called
        assert mock_logger_info.call_count >= 3
        assert "Skills for squad" in str(mock_logger_info.call_args_list[0])
        for i in range(1, squad.members + 1):
            member_name = f"Member_{i}"
            assert member_name in str(mock_logger_info.call_args_list)

    @patch.object(SelfImprovementSquad, '_simulate_task_performance')
    @patch.object(logger, 'info')
    def test_perform_task(self, mock_logger_info, mock_simulate_task_performance, squad):
        task_name = "Code a feature"
        task_complexity = 3
        squad.perform_task(task_name, task_complexity)
        mock_logger_info.assert_any_call(f"Performing task: {task_name}, Complexity: {task_complexity}")
        mock_simulate_task_performance.assert_called_once_with(task_name, task_complexity)
        mock_logger_info.assert_any_call(f"Task '{task_name}' completed successfully.")


    @patch.object(SelfImprovementSquad, '_determine_skill_for_task')
    @patch.object(SelfImprovementSquad, '_calculate_success_chance')
    @patch.object(SelfImprovementSquad, '_improve_skill')
    @patch.object(SelfImprovementSquad, '_degrade_skill')
    @patch.object(logger, 'info')
    @patch.object(logger, 'warning')
    @patch('random.random')
    @patch('time.sleep')
    def test__simulate_task_performance_success(self, mock_time_sleep, mock_random, mock_logger_warning, mock_logger_info, mock_degrade_skill, mock_improve_skill, mock_calculate_success_chance, mock_determine_skill_for_task, squad):
        mock_determine_skill_for_task.return_value = "coding"
        mock_calculate_success_chance.return_value = 0.8
        mock_random.return_value = 0.5  # Simulate success
        squad._simulate_task_performance("Code a feature", 3)
        assert mock_logger_info.called
        mock_improve_skill.assert_called()
        mock_degrade_skill.assert_not_called()
        mock_time_sleep.assert_called()


    @patch.object(SelfImprovementSquad, '_determine_skill_for_task')
    @patch.object(SelfImprovementSquad, '_calculate_success_chance')
    @patch.object(SelfImprovementSquad, '_improve_skill')
    @patch.object(SelfImprovementSquad, '_degrade_skill')
    @patch.object(logger, 'info')
    @patch.object(logger, 'warning')
    @patch('random.random')
    @patch('time.sleep')
    def test__simulate_task_performance_failure(self, mock_time_sleep, mock_random, mock_logger_warning, mock_logger_info, mock_degrade_skill, mock_improve_skill, mock_calculate_success_chance, mock_determine_skill_for_task, squad):
        mock_determine_skill_for_task.return_value = "coding"
        mock_calculate_success_chance.return_value = 0.2
        mock_random.return_value = 0.8  # Simulate failure
        squad._simulate_task_performance("Code a feature", 3)
        assert mock_logger_warning.called
        mock_improve_skill.assert_not_called()
        mock_degrade_skill.assert_called()
        mock_time_sleep.assert_called()

    def test__determine_skill_for_task_coding(self, squad):
        assert squad._determine_skill_for_task("Code something") == "coding"

    def test__determine_skill_for_task_debugging(self, squad):
        assert squad._determine_skill_for_task("Debug something") == "debugging"

    def test__determine_skill_for_task_testing(self, squad):
        assert squad._determine_skill_for_task("Test something") == "testing"

    def test__determine_skill_for_task_other(self, squad):
        skill = squad._determine_skill_for_task("Other task")
        assert skill in ("coding", "debugging", "testing")


    def test__calculate_success_chance(self, squad):
        assert squad._calculate_success_chance(3, 2) == 0.25
        assert squad._calculate_success_chance(5, 10) == -0.0
        assert squad._calculate_success_chance(1, 1) == 0.05
    
    def test__calculate_success_chance_edge_cases(self, squad):
        assert squad._calculate_success_chance(0, 0) == -0.0
        assert squad._calculate_success_chance(5, 0) == 0.45

    @patch.object(logger, 'info')
    def test__improve_skill(self, mock_logger_info, squad):
        member_name = "Member_1"
        skill = "coding"
        initial_skill_level = squad.member_skills[member_name][skill]
        squad._improve_skill(member_name, skill)
        assert squad.member_skills[member_name][skill] == min(5, initial_skill_level + 1)
        assert mock_logger_info.called
        assert f"{member_name} improved {skill} to level" in str(mock_logger_info.call_args)


    @patch.object(logger, 'info')
    def test__degrade_skill(self, mock_logger_info, squad):
        member_name = "Member_1"
        skill = "coding"
        initial_skill_level = squad.member_skills[member_name][skill]
        squad._degrade_skill(member_name, skill)
        assert squad.member_skills[member_name][skill] == max(1, initial_skill_level - 1)
        assert mock_logger_info.called
        assert f"{member_name} degraded {skill} to level" in str(mock_logger_info.call_args)


    @patch.object(SelfImprovementSquad, 'perform_task')
    @patch('time.time')
    @patch('time.sleep')
    @patch.object(logger, 'info')
    def test_run_sprint(self, mock_logger_info, mock_sleep, mock_time, mock_perform_task, squad):
        sprint_duration = 2
        tasks = [("Code feature", 3), ("Debug issue", 2)]
        mock_time.side_effect = [0, 1, 2, 3] # Simulate time passing
        squad.run_sprint(sprint_duration, tasks)
        mock_logger_info.assert_any_call(f"Starting sprint for {squad.squad_name} lasting {sprint_duration} seconds.")
        mock_perform_task.assert_called()
        mock_logger_info.assert_any_call(f"Sprint completed for {squad.squad_name}.")
        assert mock_perform_task.call_count >= 1