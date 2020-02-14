import boto3
import io
import zipfile
import mimetypes
import json

def lambda_handler(event, context):

    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:392922938890:deployPortfolioTopic')

    try:
        s3 = boto3.resource('s3')

        portfolio_bucket = s3.Bucket('portfolio.ktulu.eu')
        build_bucket = s3.Bucket('portfolio.ktulu.eu-build')

        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('portfolio-build.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                print('Extract and upload file:' + nm)
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(Subject='Portfolio app deployed', Message='Portfolio application deployed successfully.')
    except:
        topic.publish(Subject='Portfolio app deploy failed', Message='Portfolio application not deployed successfully.')
        raise

    return {
        'statusCode': 200,
        'body': json.dumps('Files uploaded to S3')
    }
