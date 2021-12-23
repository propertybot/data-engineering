import json
import boto3

def start_model(project_arn, model_arn, version_name, min_inference_units):

    client=boto3.client('rekognition')

    try:
        # Start the model
        print('Starting model: ' + model_arn)
        response=client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])

        #Get the running status
        describe_response=client.describe_project_versions(ProjectArn=project_arn,
            VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage']) 
    except Exception as e:
        print(e)
        
    print('Done...')


def start_room_classifier():
    project_arn='arn:aws:rekognition:us-east-1:735074111034:project/PropertyBot-v3-room-rekognition/1630820983471'
    model_arn='arn:aws:rekognition:us-east-1:735074111034:project/PropertyBot-v3-room-rekognition/version/PropertyBot-v3-room-rekognition.2021-09-04T22.57.53/1630821474130'
    min_inference_units=1 
    version_name='PropertyBot-v3-room-rekognition.2021-09-04T22.57.53'
    start_model(project_arn, model_arn, version_name, min_inference_units)
    return None
    



def lambda_handler(event, context):
    # TODO implement
    start_room_classifier()
    print("INFO: started room classifier")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
