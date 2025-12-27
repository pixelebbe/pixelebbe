from app import app, db
from database import Color, Role, SubmitMethod
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
    

    for role in ['api', 'users', 'events', 'edit', 'rate', 'nocache']:
        db.session.add(Role(name=role))

    for sm in [
        { "title": "in person", "file_name": "personal", "default_options": '{"name": "...", "identify": "...", "limits": "..."}' },
        { "title": "phone call (manual)", "file_name": "phone_manual", "default_options": '{"number": "...", "mnemonic": "..."}' },
        { "title": "via chaospost", "file_name": "chaospost", "default_options": '{"address_field": "..."}' },
        { "title": "via fax", "file_name": "fax", "default_options": '{"fax_no": "...", "mnemonic": "...", "template_url": "..."}' },
        { "title": "phone call (phonetree)", "file_name": "phone_tree", "default_options": '{"number": "...", "mnemonic": "..."}' },
        { "title": "assembly", "file_name": "assembly", "default_options": '{"name": "...", "location": "..."}' }
        ]:
        db.session.add(SubmitMethod(title=sm['title'], file_name=sm['file_name'],
                                    default_options=sm['default_options'], active=True))

    db.session.commit()

print("OK.")