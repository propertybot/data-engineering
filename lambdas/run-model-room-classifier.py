import json
import boto3
import io

s3 = boto3.resource('s3')

def show_custom_labels(model,bucket,photo, min_confidence):
    client=boto3.client('rekognition')

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    # For object detection use case, uncomment below code to display image.
    # display_image(bucket,photo,response)

    return response['CustomLabels']





def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print(f"INFO: received event from s3: s3://{bucket}/{key}")
    
    
    bucket=bucket
    photo=key
    model='arn:aws:rekognition:us-east-1:735074111034:project/PropertyBot-v3-room-rekognition/version/PropertyBot-v3-room-rekognition.2021-09-04T22.57.53/1630821474130'
    min_confidence=75
    
    # the confidence level above will determine if the model return any values
    try: 

        labels=show_custom_labels(model,bucket,photo, min_confidence)
        label = labels[0]['Name']
        
        if label == "Front Yard":
            print("INFO: moving to pb-images-front-yard")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-front-yard', key)
        elif label == "Attict":
            print("INFO: moving to pb-images-attict")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-attict', key)
        elif label == "Back yard":
            print("INFO: moving to pb-images-back-yard")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-back-yard', key)
        elif label == "Basement":
            print("INFO: moving to pb-images-basement")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-basement', key)
            
        elif label == "Bathroom":
            print("INFO: moving to pb-images-bathroom")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-bathroom', key)
        elif label == "Bedroom":
            print("INFO: moving to pb-images-bedroom")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-bedroom', key)
        elif label == "Dining Room":
            print("INFO: moving to pb-images-dining-room")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-dining-room', key)
        elif label == "Garage":
            print("INFO: moving to pb-images-garage")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-garage', key)
        elif label == "Kitchen":
            print("INFO: moving to pb-images-kitchen")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-kitchen', key)
        elif label == "Living Room":
            print("INFO: moving to pb-images-living-room")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-living-room', key)
        elif label == "Storage/Closet":
            print("INFO: moving to pb-images-closet-storage")
            copy_source = {
                'Bucket': bucket,
                'Key': key
             }
            s3.meta.client.copy(copy_source, 'pb-images-closet-storage', key)
        else:
            print("WARNING: model did not find/return label and image was not copied over.")
    except:
        print("WARNING: no label detected in image with a high degree of confidence")
        
        
    
    
    
    
    return {
        'statusCode': 200
    }
