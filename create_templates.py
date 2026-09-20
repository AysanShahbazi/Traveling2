# create_templates.py - Run this in your project directory

import os

BASE_DIR = r'C:\Users\Radical System\Desktop\TRAVEL\travel_site\templates'

templates = {
    'admin/dashboard.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>Admin Dashboard</h1>
        <div class="row mt-4">
            <div class="col-md-3"><div class="card bg-primary text-white p-3"><h5>Banners</h5><h2>{{ banners_count }}</h2><a href="{% url 'pages:manage_banners' %}" class="text-white">Manage</a></div></div>
            <div class="col-md-3"><div class="card bg-success text-white p-3"><h5>Destinations</h5><h2>{{ destinations_count }}</h2><a href="{% url 'pages:manage_destinations' %}" class="text-white">Manage</a></div></div>
            <div class="col-md-3"><div class="card bg-warning text-white p-3"><h5>Services</h5><h2>{{ services_count }}</h2><a href="{% url 'pages:manage_services' %}" class="text-white">Manage</a></div></div>
            <div class="col-md-3"><div class="card bg-info text-white p-3"><h5>Blog Posts</h5><h2>{{ blog_posts_count }}</h2><a href="{% url 'pages:manage_blogs' %}" class="text-white">Manage</a></div></div>
        </div>
        <a href="{% url 'pages:index' %}" class="btn btn-primary mt-3">View Website</a>
        <a href="{% url 'pages:logout' %}" class="btn btn-danger mt-3">Logout</a>
    </div>
</body>
</html>''',

    'admin/banners/list.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Manage Banners</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>Banners</h1>
        <a href="{% url 'pages:add_banner' %}" class="btn btn-primary mb-3">Add Banner</a>
        <a href="{% url 'pages:admin_dashboard' %}" class="btn btn-secondary mb-3">Back to Dashboard</a>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
        
        <table class="table">
            <thead><tr><th>Title</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
                {% for banner in banners %}
                <tr>
                    <td>{{ banner.title }}</td>
                    <td>{% if banner.is_active %}Active{% else %}Inactive{% endif %}</td>
                    <td>
                        <a href="{% url 'pages:edit_banner' banner.pk %}" class="btn btn-sm btn-warning">Edit</a>
                        <a href="{% url 'pages:delete_banner' banner.pk %}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?')">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>''',

    'admin/banners/form.html': '''<!DOCTYPE html>
<html>
<head>
    <title>{{ action }} Banner</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>{{ action }} Banner</h1>
        <form method="POST" enctype="multipart/form-data">
            {% csrf_token %}
            <div class="mb-3">
                <label>Title</label>
                <input type="text" name="title" class="form-control" value="{{ banner.title|default:'' }}" required>
            </div>
            <div class="mb-3">
                <label>Subtitle</label>
                <input type="text" name="subtitle" class="form-control" value="{{ banner.subtitle|default:'' }}" required>
            </div>
            <div class="mb-3">
                <label>Description</label>
                <textarea name="description" class="form-control" required>{{ banner.description|default:'' }}</textarea>
            </div>
            <div class="mb-3">
                <label>Image</label>
                {% if banner.background_image %}<div><img src="{{ banner.background_image.url }}" style="max-height:100px"></div>{% endif %}
                <input type="file" name="background_image" class="form-control">
            </div>
            <div class="mb-3">
                <label><input type="checkbox" name="is_active" {% if banner.is_active|default:True %}checked{% endif %}> Active</label>
            </div>
            <button type="submit" class="btn btn-primary">Save</button>
            <a href="{% url 'pages:manage_banners' %}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</body>
</html>''',

    'admin/destinations/list.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Manage Destinations</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>Destinations</h1>
        <a href="{% url 'pages:add_destination' %}" class="btn btn-primary mb-3">Add Destination</a>
        <a href="{% url 'pages:admin_dashboard' %}" class="btn btn-secondary mb-3">Dashboard</a>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
        
        <table class="table">
            <thead><tr><th>Name</th><th>Location</th><th>Price</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
                {% for destination in destinations %}
                <tr>
                    <td>{{ destination.name }}</td>
                    <td>{{ destination.location }}</td>
                    <td>${{ destination.price }}</td>
                    <td>{% if destination.is_active %}Active{% else %}Inactive{% endif %}</td>
                    <td>
                        <a href="{% url 'pages:edit_destination' destination.pk %}" class="btn btn-sm btn-warning">Edit</a>
                        <a href="{% url 'pages:delete_destination' destination.pk %}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?')">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>''',

    'admin/destinations/form.html': '''<!DOCTYPE html>
<html>
<head>
    <title>{{ action }} Destination</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>{{ action }} Destination</h1>
        <form method="POST" enctype="multipart/form-data">
            {% csrf_token %}
            <div class="mb-3">
                <label>Name</label>
                <input type="text" name="name" class="form-control" value="{{ destination.name|default:'' }}" required>
            </div>
            <div class="mb-3">
                <label>Location</label>
                <input type="text" name="location" class="form-control" value="{{ destination.location|default:'' }}" required>
            </div>
            <div class="mb-3">
                <label>Price</label>
                <input type="number" step="0.01" name="price" class="form-control" value="{{ destination.price|default:'' }}" required>
            </div>
            <div class="mb-3">
                <label>Description</label>
                <textarea name="description" class="form-control">{{ destination.description|default:'' }}</textarea>
            </div>
            <div class="mb-3">
                <label>Display Order</label>
                <input type="number" name="order" class="form-control" value="{{ destination.order|default:'0' }}">
            </div>
            <div class="mb-3">
                <label>Image</label>
                {% if destination.image %}<div><img src="{{ destination.image.url }}" style="max-height:100px"></div>{% endif %}
                <input type="file" name="image" class="form-control">
            </div>
            <div class="mb-3">
                <label><input type="checkbox" name="is_active" {% if destination.is_active|default:True %}checked{% endif %}> Active</label>
            </div>
            <button type="submit" class="btn btn-primary">Save</button>
            <a href="{% url 'pages:manage_destinations' %}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</body>
</html>''',

    'admin/services/list.html': '''<!DOCTYPE html>
<html>
<head>
    <title>Manage Services</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>Services</h1>
        <a href="{% url 'pages:add_service' %}" class="btn btn-primary mb-3">Add Service</a>
        <a href="{% url 'pages:admin_dashboard' %}" class="btn btn-secondary mb-3">Dashboard</a>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
        
        <table class="table">
            <thead><tr><th>Title</th><th>Link</th><th>Order</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
                {% for service in services %}
                <tr>
                    <td>{{ service.title }}</td>
                    <td>{{ service.link }}</td>
                    <td>{{ service.order }}</td>
                    <td>{% if service.is_active %}Active{% else %}Inactive{% endif %}</td>
                    <td>
                        <a href="{% url 'pages:edit_service' service.pk %}" class="btn btn-sm btn-warning">Edit</a>
                        <a href="{% url 'pages:delete_service' service.pk %}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?')">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>''',

    'admin/services/form.html': '''<!DOCTYPE html>
<html>
<head>
    <title>{{ action }} Service</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>{{ action }} Service</h1>
        <form method="POST" enctype="multipart/form-data">
            {% csrf_token %}
            <div class="mb-3">
                <label>Title</label>
                <input type="text" name="title" class="form-control" value="{{ service.title|default:'' }}" required>
            </div>
            <div class="mb-3">
                <label>Description</label>
                <textarea name="description" class="form-control" required>{{ service.description|default:'' }}</textarea>
            </div>
            <div class="mb-3">
                <label>Link</label>
                <input type="url" name="link" class="form-control" value="{{ service.link|default:'' }}">
            </div>
            <div class="mb-3">
                <label>Order</label>
                <input type="number" name="order" class="form-control" value="{{ service.order|default:'0' }}">
            </div>
            <div class="mb-3">
                <label>Image</label>
                {% if service.image %}<div><img src="{{ service.image.url }}" style="max-height:100px"></div>{% endif %}
                <input type="file" name="image" class="form-control">
            </div>
            <div class="mb-3">
                <label><input type="checkbox" name="is_active" {% if service.is_active|default:True %}checked{% endif %}> Active</label>
            </div>
            <button type="submit" class="btn btn-primary">Save</button>
            <a href="{% url 'pages:manage_services' %}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</body>
</html>''',
}

# Create directories and files
for path, content in templates.items():
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created: {full_path}')

print('\nAll templates created successfully!')