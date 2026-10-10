from sqlmodel import Session, text


def test_isolated_test_database(db_session: Session):
    result = db_session.exec(
        text("SELECT current_database()")
    ).one()

    assert result[0] == "mini_erp_test"