import streamlit as st
from bs4 import BeautifulSoup
import requests
import os
import openai
import json
from usellm import Message, Options, UseLLM
from PIL import Image
# openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    #st.title("AutoMind")
    logo_image = Image.open("Images/img_1.png")
    st.sidebar.image(logo_image, use_column_width=True)
    st.sidebar.markdown("&nbsp;")
    option = st.sidebar.selectbox("Select an option", ("Car Comparison", "Car Inspection"))
    # Option 1: Comparison
    if option == "Car Comparison":
        compare_cars()
    # Option 2: Inspection
    elif option == "Car Inspection":
        inspect_car()

def openai_prompt2(data):
    
    if data["oil_back"] == "No":
        
        message=("""Since, the proposed car failed the Oil Back Compression Test, it indicates serious engine problems, 
                 resulting in reduced performance, decreased fuel efficiency, increased emissions, costly repairs, 
                 and unreliable operation. Oil in the combustion chamber damages the engine's internal components, 
                 leading to poor power output and potential engine failure. It also causes incomplete fuel burning, 
                 resulting in higher fuel consumption. The increased emissions contribute to environmental pollution 
                 and potential compliance issues. Repairing oil back compression is expensive and time-consuming. 
                 Overall, it's best to find a car with a well-maintained engine for reliability and a better ownership experience""")
        
        st.write(message)
        
    else:

        # Initialize the service
        service = UseLLM(service_url="https://usellm.org/api/llm")

        user_prompt = data
        # Prepare the conversation
        messages = [
            Message(role="system", content = "You are a bot named AutoMind, " +
                                            "an intelligent LLM assistant in automotive domain, " +
                                            "that inspects the condition of cars based on the following characteristics on which you need "+
                                            "to make a calculated decision and tell whether the decision to buy the car is good or not. "+
                                            "The user input a list of question and answers for you to understand the condition of the car to make an informed decision" +
                                            "You have to explicitly give one choice as the response" +
                                            "Explain your reasoning in detail and in a point-wise manner such that would convince me"),
            Message(role="user", content = json.dumps(user_prompt))
            ]
        
        if "follow up question" in data:

            # messages.append(Message(role="user", content = "I also have a follow up question : " + data["follow up question"]))
            messages = [
                Message(role="system", content = "You are a bot named AutoMind, " +
                                            "an intelligent LLM assistant in automotive domain, " +
                                            "that inspects the condition of cars based on the following characteristics on which you need "+
                                            "to make a calculated decision and tell whether the decision to buy the car is good or not. "+
                                            "The user input a list of question and answers for you to understand the condition of the car to make an informed decision" +
                                            "The inputs were - " +
                                            json.dumps(user_prompt) +
                                            "you already responded with the below detailed and point-wise response to convince the user of your explicit choice" +
                                            json.dumps(data["prev_resp"]) +
                                            "\n Now the user has a follow up question: " +
                                            data["follow up question"] +
                                            "Please respond with a sensible and crisp logical answer")
                      ]


        options = Options(messages=messages)

        # Interact with the service
        response = service.chat(options)

        # Print the assistant's response
        st.write(response.content)


def openai_prompt(data):
    # Initialize the service
    service = UseLLM(service_url="https://usellm.org/api/llm")

    template = '''
    
    Make year: {make_year}
    Registration year: {registration_year}
    Fuel type: {fuel_type}
    Km driven: {km_driven}
    Transmission: {transmission}
    No. of Owner: {owner}
    
    '''

    user_prompt = ""
    for d in data:
        user_prompt += template.format(
                                        make_year=d["Make year"],
                                        registration_year=d["Registration year"],
                                        fuel_type=d["Fuel type"],
                                        km_driven=d["Km driven"],
                                        transmission=d["Transmission"],
                                        owner=d["No. of Owner"]
                                    )

    # Prepare the conversation
    messages = [
        Message(role="system", content = "You are a bot named AutoMind, " +
                                         "an intelligent LLM assistant in automotive domain. " +
                                         "You need to tell me which car is a better choice based on the following parameters." +
                                         "Things to keep in mind: " +
                                         "If the make is Honda - it generally makes better petrol engines" +
                                         "If the make is Hyundai - it makes better diesel engines" +
                                         "If the make contains Suzuki - it gives better mileage and has lower running costs" +
                                         "You have to explicitly give one choice as the response" +
                                         "Explain your reasoning in detail and in a point-wise manner such that would convince me"),
        Message(role="user", content = user_prompt)
        ]

    options = Options(messages=messages)

    # Interact with the service
    response = service.chat(options)

    # Print the assistant's response
    return(response.content)


def compareCarsSpinny(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {}
    car_name = soup.find('h1', class_='DesktopRightSection__carName').text.strip()
    data["car_name"] = car_name
    image_urls = soup.select_one('.styles__carouselImage')
    image_url = image_urls['src'] if image_urls else None
    image_url = ("https:" + image_url)
    overview_items = soup.select('.DesktopOverview__overviewItem')
    for item in overview_items:
        label = item.select_one('.DesktopOverview__itemLabel').text.strip()
        value = item.select_one('.DesktopOverview__itemDisplay').text.strip()
        data[label] = value
        data["image"] = image_url
    return data

def compare_cars():
    st.markdown("<h1 style='text-align: center;'>AutoMind Comparison</h1>", unsafe_allow_html=True)
    with st.form("url_form"):
        url1 = st.text_input("Enter URL 1:")
        url2 = st.text_input("Enter URL 2:")

        # Submit button within the form
        form_submit = st.form_submit_button(label='Compare Cars')
    if form_submit:
        if url1 and url2:
            car1_data = compareCarsSpinny(url1)
            car2_data = compareCarsSpinny(url2)
            # st.image(car1_data["image"], use_column_width=True)
            # st.image(car2_data["image"], use_column_width=True)
            # Create two columns for the table
            col1, col2 = st.columns(2)

            # Display images in each column
            # with col1:
            #     st.image(car1_data["image"], use_column_width=True)
            #     st.subheader("Car 1 Details")
            #     car1 = [f"{key}: {value}" for key, value in car1_data.items() if key != "image"]
            #     st.write("\n".join(car1))
            #
            # with col2:
            #     st.image(car2_data["image"], use_column_width=True)
            #     st.subheader("Car 2 Details")
            #     car2 = [f"{key}: {value}" for key, value in car2_data.items() if key != "image"]
            #     st.write("\n".join(car2))

            with col1:
                st.image(car1_data["image"], use_column_width=True)
                st.write("<b>" + str(car1_data["car_name"]) + "</b>", unsafe_allow_html=True)
                car1 = [(key, value) for key, value in car1_data.items() if
                        key != "image" and key != "car_name"]
                st.markdown("<div style='border: 1px solid black; padding: 10px;'>"
                            "<table style='border-collapse: collapse; width: 100%;'>"
                            "<caption style='caption-side: top; text-align: center; font-weight: bold;'>Car Overview</caption>"
                            + ''.join(
                    f"<tr><td style='border-bottom: 1px solid black; padding: 5px; text-align: left;'><b>{key}</b></td>"
                    f"<td style='border-bottom: 1px solid black; padding: 5px; text-align: left;'>{value}</td></tr>"
                    for key, value in car1) +
                            "</table></div>", unsafe_allow_html=True)

            with col2:
                st.image(car2_data["image"], use_column_width=True)
                st.write("<b>" + str(car2_data["car_name"]) + "</b>", unsafe_allow_html=True)
                car2 = [(key, value) for key, value in car2_data.items() if
                        key != "image" and key != "car_name"]
                st.markdown("<div style='border: 1px solid black; padding: 10px;'>"
                            "<table style='border-collapse: collapse; width: 100%;'>"
                            "<caption style='caption-side: top; text-align: center; font-weight: bold;'>Car Overview</caption>"
                            + ''.join(
                    f"<tr><td style='border-bottom: 1px solid black; padding: 5px; text-align: left;'><b>{key}</b></td>"
                    f"<td style='border-bottom: 1px solid black; padding: 5px; text-align: left;'>{value}</td></tr>"
                    for key, value in car2) +
                            "</table></div>", unsafe_allow_html=True)
            st.write(openai_prompt([car1_data, car2_data]))

def inspect_car():
    st.markdown("<h1 style='text-align: center;'>AutoMind Inspection</h1>", unsafe_allow_html=True)
    
    # Create an empty dictionary to store responses
    responses = {}
    
    # Define the questions
    questions = [
        "Which brand is the car?",
        "Which model is the car?",
        "Which year was the car registered?",
        "How many kilometers has the car driven?",
        "What is the price being quoted?"
    ]
    
    # Iterate over the questions and ask the user for responses
    for question in questions:
        response = st.text_input(question)
        responses[question] = response
    
    # Store the responses in a dictionary
    data = {
        "brand": responses["Which brand is the car?"],
        "model": responses["Which model is the car?"],
        "year": responses["Which year was the car registered?"],
        "kilometers": responses["How many kilometers has the car driven?"],
        "price": responses["What is the price being quoted?"]
    }
    
    # Display the Body section
    st.title("Body")
    
    
    st.subheader("Door Panel")
    door_panel_options = ["Yes", "No"]
    selected_door_panel = st.radio("Are there any scratches on the door panel?", door_panel_options)
    st.image("./images/IMG_3939.JPG", caption="Door Panel", use_column_width=True)
    data["door_panel"] = selected_door_panel

    st.subheader("Door Frame")
    door_frame_options = ["Yes", "No"]
    selected_door_frame = st.radio("Are there any scratches on the door frame?", door_frame_options)
    st.image("./images/IMG_3935.JPG", caption="Door Frame", use_column_width=True)
    data["door_frame"] = selected_door_frame

    st.subheader("Side Dashboard Vent Area")
    side_dashboard_options = ["Yes", "No"]
    selected_side_dashboard = st.radio("Are there any scratches in this region?", side_dashboard_options)
    st.image("./images/IMG_3937.JPG", caption="Side Dashboard Vent Area", use_column_width=True)
    data["side_dashboard"] = selected_side_dashboard

    st.subheader("Depressed Pedals")
    pedals_options = ["Yes", "No"]
    selected_pedals = st.radio("Is the gas pedal depressed?", pedals_options)
    st.image("./images/pedal.jpg", caption="Depressed Gas Pedal", use_column_width=True)
    data["pedals"] = selected_pedals

    st.subheader("Tires")
    tires_options = ["Yes", "No"]
    selected_tires = st.radio("Are the tires worn out?", tires_options)
    st.image("./images/tire.jpg", caption="Tire Wear Checkup", use_column_width=True)
    data["tires"] = selected_tires

    st.subheader("Paint Mismatch")
    paint_options = ["Yes", "No"]
    selected_paint = st.radio("Is there a mismatch of paint on any unit?", paint_options)
    st.image("./images/IMG_3945.JPG", caption="Paint Mismatch", use_column_width=True)
    data["paint"] = selected_paint

    st.subheader("Panel Gaps")
    panel_options = ["Yes", "No"]
    selected_panel = st.radio("Is there gap observed between the panels?", panel_options)
    st.image("./images/IMG_3943.JPG", caption="Body Panels", use_column_width=True)
    data["panel"] = selected_panel

    st.subheader("Oil Quality")
    oil_options = ["Healthy", "Top-up", "Unhealthy"]
    oil_panel = st.radio("What is the color of the oil?", oil_options)
    st.image("./images/oil.jpg", caption="Oil Tip", use_column_width=True)
    data["oil"] = oil_panel

    st.subheader("Coolant Level")
    coolant_options = ["Yes", "No"]
    coolant_panel = st.radio("Is the coolant reservoir topped up?", coolant_options)
    st.image("./images/IMG_3944.JPG", caption="Coolant Reservoir", use_column_width=True)
    data["coolant"] = coolant_panel
    
    st.subheader("Coolant Color")
    coolant_color_options = ["Green", "Blue", "Pink", "Colorless"]
    coolant_color_panel = st.radio("What is color of the coolant?", coolant_color_options)
    data["coolant_color"] = coolant_color_panel

    st.subheader("Spare Tire")
    spare_options = ["Used", "Unused"]
    spare_panel = st.radio("Is the spare tire in used or unused condition?", spare_options)
    st.image("./images/Spare.jpg", caption="If the blue and red line on the tire is visible that means the tire is unused", use_column_width=True)
    data["spare_tire"] = spare_panel

    st.title("Electricals")

    st.subheader("Headlight (High-beam)")
    highbeam_options = ["Yes", "No"]
    highbeam_panel = st.radio("Is the high-beam turning on?", highbeam_options)
    st.image("./images/highbeam.jpg", caption="High Beam", use_column_width=True)
    data["high_beam"] = highbeam_panel

    st.subheader("Headlight (Low-beam)")
    lowbeam_options = ["Yes", "No"]
    lowbeam_panel = st.radio("Is the low-beam turning on?", lowbeam_options)
    st.image("./images/lowbeam.jpg", caption="Low Beam", use_column_width=True)
    data["low_beam"] = lowbeam_panel

    st.subheader("Fog Lamp")
    foglamp_options = ["Yes", "No"]
    foglamp_panel = st.radio("Are the fog lamps turning on?", foglamp_options)
    st.image("./images/fog.jpg", caption="Fog Lamp", use_column_width=True)
    data["fog_lamp"] = foglamp_panel

    st.subheader("Tail Lamp")
    brakelight_options = ["Yes", "No"]
    brakelight_panel = st.radio("Are the tail lamps turning on?", brakelight_options)
    st.image("./images/tail.png", caption="Tail Lamp and Reverse Lights", use_column_width=True)
    data["tail_lamp"] = brakelight_panel

    st.subheader("Reverse Lights")
    reverselight_options = ["Yes", "No"]
    reverselight_panel = st.radio("Are the reverse lights turning on?", reverselight_options)
    data["reverse_light"] = reverselight_panel

    st.subheader("Front Windows")
    frontwindows_options = ["Yes", "No"]
    frontwindows_panel = st.radio("Are you able to roll up/down the front windows?", frontwindows_options)
    st.image("./images/window.jpg", caption="Front & Rear Windows", use_column_width=True)
    data["front_windows"] = frontwindows_panel

    st.subheader("Rear Windows")
    rearwindows_options = ["Yes", "No"]
    rear_windows_panel = st.radio("Are you able to roll up/down the rear windows?", rearwindows_options)
    data["rear_windows"] = rear_windows_panel

    st.subheader("Windshield Wipers")
    wipers_options = ["Yes", "No"]
    wipers_panel = st.radio("Are you able to turn on/off the wipers?", wipers_options)
    st.image("./images/wiper.png", caption="Windshield Wipers", use_column_width=True)
    data["wipers"] = wipers_panel

    st.subheader("ORVMs")
    orvm_options = ["Yes", "No"]
    orvm_panel = st.radio("Are you able to fold/unfold the ORVMs?", orvm_options)
    st.image("./images/orvm.png", caption="ORVM", use_column_width=True)
    data["orvm"] = orvm_panel


    st.title("Dashboard")

    st.subheader("Engine Light")
    engine_light_options = ["Yes", "No"]
    engine_light_panel = st.radio("Is the check engine light on?", engine_light_options)
    st.image("./images/engine.jpg", caption="Check Engine Light", use_column_width=True)
    data["engine_light"] = engine_light_panel

    st.subheader("Temperature Light")
    temp_light_options = ["Yes", "No"]
    temp_light_panel = st.radio("Is the temperature light on?", temp_light_options)
    st.image("./images/temp.jpg", caption="Temperature Light", use_column_width=True)
    data["temp_light"] = temp_light_panel

    st.subheader("Oil Light")
    oil_light_options = ["Yes", "No"]
    oil_light_panel = st.radio("Is the oil light on?", oil_light_options)
    st.image("./images/oil-light.jpg", caption="Oil Light", use_column_width=True)
    data["oil_light"] = oil_light_panel

    st.subheader("Battery Light")
    battery_light_options = ["Yes", "No"]
    battery_light_panel = st.radio("Is the battery light on?", battery_light_options)
    st.image("./images/battery.png", caption="Battery Light", use_column_width=True)
    data["battery_light"] = battery_light_panel

    st.subheader("Airbag Light")
    airbag_light_options = ["Yes", "No"]
    airbag_light_panel = st.radio("Is the airbag light on?", airbag_light_options)
    st.image("./images/airbag.jpg", caption="Airbag Light", use_column_width=True)
    data["airbag_light"] = airbag_light_panel

    st.title("Oil Back Compression Test")
    st.write("Step 1: Turn on the car")
    st.image("./images/start.png", caption="Start Engine", use_column_width=True)
    st.write("Step 2: Remove the oil dipstick")
    st.image("./images/IMG_3952.jpg", caption="Remove the Dipstick", use_column_width=True)
    st.write("Step 3: Place a piece of paper on the outlet from where dipstick was removed")
    st.image("./images/IMG_3955.jpg", caption="Place the paper at the nozzle", use_column_width=True)
    oil_back_options = ["Yes", "No"]
    oil_back_panel = st.radio("Is the paper spotless?", oil_back_options)
    data["oil_back"] = oil_back_panel

    if st.checkbox("Submit"):
        reply = openai_prompt2(data)
        reply_cont = st.container()
        # reply_cont.write('spme reply')
        data_cont = st.container()
        data_new_var = data_cont.text_input(label='Ask a followup question')
        data["prev_resp"] = reply
        data["follow up question"] = data_new_var

        if st.checkbox('Submit more') and data_new_var is not None:
            openai_prompt2(data)
        
            # st.write(another_reply)
            
        
        

if __name__ == "__main__":
    main()
