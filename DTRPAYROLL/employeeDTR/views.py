from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Employee, DTR
from .forms import UploadFileForm, DTRForm
from django.contrib import messages
from computest import calculate_payroll
import pandas as pd
from django.utils import timezone
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import json
import ast
from django.utils.timezone import now

def generate_pdf_payroll_view(request):
    try:
        if request.method == 'POST':
            # Get the payroll data from the POST request
            payroll_data_literal = request.POST.get('PaySlip_Data', '')

            # Ensure that we have data to put into our context
            if not payroll_data_literal:
                raise ValueError("No PaySlip data provided.")

           # If we have a string, try to safely convert it to a Python object
            if isinstance(payroll_data_literal, str):
                try:
                    PaySlip_Data = ast.literal_eval(payroll_data_literal)
                except (ValueError, SyntaxError) as e:
                    logging.error(f"Error converting string to Python object: {e}")
                    return HttpResponse("Error parsing PaySlip data.")
            else:
                # If it's not a string, then use it as is (should be a dictionary)
                PaySlip_Data = payroll_data_literal

            # Render the HTML template with the PaySlip data
            html_string = render_to_string('PaySlip_Template.html', {'PaySlip_Data': PaySlip_Data})

            # Generate PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="payroll_results.pdf"'
            result = pisa.CreatePDF(html_string, dest=response)

            if result.err:
                logging.error(f"Error in PDF generation: {result.err}")
                return HttpResponse("Error generating PDF.")

            return response
        else:
            return HttpResponse("Invalid request method.")
    except Exception as e:
        logging.error(f"Unexpected error in PDF generation: {e}")
        return HttpResponse("Error generating PDF.")

def custom_login(request):
    if request.user.is_authenticated:
        if request.user.employee.department.department_name.lower() == 'hr':
            return redirect('hr_dashboard')
        else:
            logout(request)
            messages.error(request, 'Access denied. Only HR can access the dashboard.')
            return redirect('custom_login')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if request.user.employee.department.department_name.lower() == 'hr':
                    return redirect('hr_dashboard')
                else:
                    logout(request)
                    messages.error(request, 'Access denied. Only HR can access the dashboard.')
                    return redirect('custom_login')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def hr_dashboard(request):
    if request.user.is_authenticated and request.user.employee.department.department_name.lower() == 'hr':
        employees = Employee.objects.all()
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(status=1).count()
        today_date = now().date()
        today_attendance = DTR.objects.filter(datetime__date=today_date, status='C/In').count()

        for employee in employees:
            employee.full_name = f"{employee.first_name} {employee.last_name}".title()
            employee.department.department_name= employee.department.department_name.title()
            employee.position.position = employee.position.position.title()

        context = {
            'employees': employees,
            "total_employees":total_employees,
            "today_attendance":today_attendance,
            "active_employees":active_employees,
            "today_date":today_date
        }

        return render(request, 'hr_dashboard.html',context)
    else:
        messages.error(request, 'You must be an HR to view this page.')
        return redirect('custom_login')

def attendance(request):
    if request.method == 'POST':
        if 'upload_excel' in request.POST:
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES['excelFile']

                try:
                # Assuming the uploaded file is in Excel format
                    df = pd.read_excel(uploaded_file)

                    # Iterate over each row in the DataFrame
                    for index, row in df.iterrows():
                        department = row['Department']
                        name = row['Name']
                        number = row['No.']  # Assuming 'No.' corresponds to employee_id
                        datetime_str = row['Date/Time']

                        # Convert datetime_str to a timezone-aware datetime object
                        if isinstance(datetime_str, pd.Timestamp):
                            datetime_obj = datetime_str.to_pydatetime()
                        else:
                            try:
                                datetime_obj = timezone.make_aware(datetime.strptime(datetime_str, '%d/%m/%Y %I:%M:%S %p'))
                            except (ValueError, TypeError):
                                datetime_obj = None

                        status = row['Status']
                        location_id = row['Location ID']
                        id_number = row['ID Number'] if not pd.isna(row['ID Number']) else None

                        # Create and save a DTR instance
                        dtr_instance = DTR.objects.create(
                            department=department,
                            name=name,
                            number=number,
                            datetime=datetime_obj,
                            status=status,
                            location_id=location_id,
                            id_number=id_number,
                        )

                    # You may add any additional processing or validation here
                    messages.success(request, 'Excel file uploaded and processed successfully.')
                except Exception as e:
                    # If an error occurs, add an error message
                    messages.error(request, f'An error occurred: {e}')
                return redirect('attendance')
        elif 'manual_submit' in request.POST:
            number = request.POST.get('employee')
            datetime_str = request.POST.get('datetime')
            status = request.POST.get('status')

            if not all([number, datetime_str, status]):
                messages.error(request, 'All fields are required.')
                return redirect('attendance')

            try:
                datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
                employee = Employee.objects.get(employee_id=number)
                department=employee.department.department_name
                name=f"{employee.first_name} {employee.last_name}".title()
                location_id=0
                id_number=None

                DTR.objects.create(
                    department=department,
                    name=name,
                    number=number,
                    datetime=datetime_obj,
                    status=status,
                    location_id=location_id,
                    id_number=id_number
                )

                messages.success(request, 'Manual DTR entry added successfully.')
                return redirect('attendance')
            except Employee.DoesNotExist:
                messages.error(request, 'Employee not found.')
                return redirect('attendance')
            except ValueError as e:
                messages.error(request, f'Invalid datetime format: {e}')
                return redirect('attendance')
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')
                return redirect('attendance')
    else:
        form = UploadFileForm()
        dtrs = DTR.objects.all().order_by('-datetime')
        for dtr in dtrs:
            emp = Employee.objects.get(employee_id=dtr.number) #instead of using PK, use the employee_id
            dtr.employee = emp
            dtr.employee.full_name = f"{emp.first_name} {emp.last_name}".title()
            dtr.employee.department.department_name= emp.department.department_name.title()
            dtr.employee.position.position = emp.position.position.title()
            dtr.datetime = dtr.datetime.strftime('%B %d, %Y %I:%M %p')
        employees = Employee.objects.filter(status=1,department_id=1) #update to dynamic
        for employee in employees:
            employee.full_name = f"{employee.first_name} {employee.last_name}".title()

        return render(request, 'attendance.html', {'form': form, "dtrs":dtrs, "employees":employees})

def payroll(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        employee_id = request.POST.get('employee')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if not all([employee_id, start_date, end_date]):
            messages.error(request, 'All fields are required.')
            return redirect('payroll')

        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

            if start_date_obj > end_date_obj:
                messages.error(request, 'End date must be after start date.')
                return redirect('payroll')

            employee = Employee.objects.get(employee_id=employee_id)

            start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1, seconds=-1)

            if action == 'payslip':
                dtr_records = DTR.objects.filter(number=employee_id, datetime__range=[start_date, end_date])
                if not dtr_records.exists():
                    messages.error(request, 'No DTR records found for the selected employee and date range.')
                    return redirect('payroll')

                payroll_data_json = calculate_payroll(dtr_records, start_date, end_date)
                payroll_data = json.loads(payroll_data_json)

                return render(request, 'generate_payslip.html', {
                    'payroll_data': payroll_data,
                    'employee_name': f"{employee.first_name} {employee.last_name}",
                    'PaySlip_Data': payroll_data[0] if payroll_data else {}
                })
            elif action == 'dtr':
                # Implement logic for generating DTR
                # dtr_data = calculate_dtr(employee_id, start_date, end_date)
                return render(request, 'generate_dtr.html', {
                    # 'dtr_data': dtr_data,
                    'employee_name': f"{employee.first_name} {employee.last_name}"
                })

        except Employee.DoesNotExist:
            messages.error(request, 'Employee not found.')
            return redirect('payroll')
        except ValueError as e:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return redirect('payroll')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('payroll')

    employees = Employee.objects.filter(department_id=1)
    for employee in employees:
        employee.full_name = f"{employee.first_name} {employee.last_name}".title()
        employee.department.department_name= employee.department.department_name.title()
        employee.position.position = employee.position.position.title()

    return render(request, 'payroll.html', {'employees': employees})

def logout_user(request):
    logout(request)
    return redirect('custom_login')


def edit_dtr(request, dtr_id):
    dtr_instance = DTR.objects.get(pk=dtr_id)
    if request.method == 'POST':
        form = DTRForm(request.POST, instance=dtr_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'DTR entry successfully edited!')
            return redirect('attendance')
    else:
        form = DTRForm(instance=dtr_instance)
    return render(request, 'edit_dtr.html', {'form': form})