from pathlib import Path
from app.analysis.repository import analyze_repository

def test_analyzes_python_modules_and_dependencies(tmp_path: Path):
    orders = tmp_path / 'services' / 'orders'
    payments = tmp_path / 'services' / 'payments'
    orders.mkdir(parents=True); payments.mkdir(parents=True)
    (orders / 'service.py').write_text('from services.payments.service import charge\n\ndef place():\n    if True:\n        return charge()\n')
    (payments / 'service.py').write_text('def charge():\n    return True\n')
    result = analyze_repository(tmp_path, 'sample')
    assert result['repository']['synthetic'] is False
    assert result['summary']['modules'] == 2
    assert result['summary']['dependencies'] == 1
    assert result['edges'][0]['source'] == 'orders'
    assert result['edges'][0]['target'] == 'payments'
