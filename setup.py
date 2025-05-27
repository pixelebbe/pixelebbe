from app import app, db
from database import Color, Role
from flask_migrate import stamp

with app.app_context():
    db.create_all()
    stamp('migrations')

    # Import colors
    for k, v in {
        'K1': '#000000',
        'K2': '#222222',
        'K3': '#444444',
        'K4': '#666666',

        'W1': '#888888',
        'W2': '#AAAAAA',
        'W3': '#CCCCCC',
        'W4': '#FFFFFF',

        'R1': '#880000',
        'R2': '#aa2222',
        'R3': '#cc4444',
        'R4': '#ff6666',

        'G1': '#008800',
        'G2': '#22aa22',
        'G3': '#44cc44',
        'G4': '#66ff66',

        'B1': '#000088',
        'B2': '#2222aa',
        'B3': '#4444cc',
        'B4': '#6666ff',

        'C1': '#008888',
        'C2': '#22aaaa',
        'C3': '#44cccc',
        'C4': '#66ffff',

        'M1': '#880088',
        'M2': '#aa22aa',
        'M3': '#cc44cc',
        'M4': '#ff66ff',

        'Y1': '#888800',
        'Y2': '#aaaa22',
        'Y3': '#cccc44',
        'Y4': '#ffff66',

        'Z9': '#nonono'
    }.items():
        hue = k[0]
        lightness = k[1]
        db.session.add(Color(hexcode=v, hue=hue, lightness=lightness))
    

    for role in ['api', 'users', 'events', 'edit', 'rate']:
        db.session.add(Role(name=role))

    db.session.commit()

print("OK.")