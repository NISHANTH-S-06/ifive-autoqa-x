"""Backend unit tests for Phase 3 Playwright action validation."""
from __future__ import annotations

import json
import pytest
from fastapi import HTTPException
from app.services.automated_execution import parse_action


def test_action_select_valid():
    step = {'action': 'SELECT', 'selector': '#dept', 'value': '1'}
    parsed = parse_action({'test_data': json.dumps(step), 'step_number': 1})
    assert parsed['action'] == 'SELECT'
    assert parsed['selector'] == '#dept'
    assert parsed['value'] == '1'


def test_action_select_missing_value():
    step = {'action': 'SELECT', 'selector': '#dept'}
    with pytest.raises(HTTPException) as exc:
        parse_action({'test_data': json.dumps(step), 'step_number': 1})
    assert exc.value.status_code == 422


def test_action_check_valid():
    step = {'action': 'CHECK', 'selector': '#active'}
    parsed = parse_action({'test_data': json.dumps(step), 'step_number': 1})
    assert parsed['action'] == 'CHECK'


def test_action_uncheck_valid():
    step = {'action': 'UNCHECK', 'selector': '#active'}
    parsed = parse_action({'test_data': json.dumps(step), 'step_number': 1})
    assert parsed['action'] == 'UNCHECK'


def test_action_wait_for_element_valid():
    step = {'action': 'WAIT_FOR_ELEMENT', 'selector': '.table-row'}
    parsed = parse_action({'test_data': json.dumps(step), 'step_number': 1})
    assert parsed['action'] == 'WAIT_FOR_ELEMENT'


def test_action_assert_value_valid():
    step = {'action': 'ASSERT_VALUE', 'selector': '#diff', 'expected': '+15'}
    parsed = parse_action({'test_data': json.dumps(step), 'step_number': 1})
    assert parsed['action'] == 'ASSERT_VALUE'
    assert parsed['expected'] == '+15'


def test_action_assert_url_valid():
    step = {'action': 'ASSERT_URL', 'expected': '/dashboard'}
    parsed = parse_action({'test_data': json.dumps(step), 'step_number': 1})
    assert parsed['action'] == 'ASSERT_URL'


def test_action_read_text_valid():
    step = {'action': 'READ_TEXT', 'selector': '#current-qty'}
    parsed = parse_action({'test_data': json.dumps(step), 'step_number': 1})
    assert parsed['action'] == 'READ_TEXT'


def test_action_assert_table_row_valid():
    step = {'action': 'ASSERT_TABLE_ROW', 'selector': 'table.directory', 'expected': 'john.doe@demo.local'}
    parsed = parse_action({'test_data': json.dumps(step), 'step_number': 1})
    assert parsed['action'] == 'ASSERT_TABLE_ROW'
