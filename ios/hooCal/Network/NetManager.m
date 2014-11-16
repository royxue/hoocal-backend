//
//  NetManager.m
//  hooCal
//
//  Created by zhongtoby on 14/11/15.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import "NetManager.h"
#import <AFNetworking.h>
#import <CocoaSecurity.h>
#import "RequestConfigure.h"

@interface NetManager ()
@property (nonatomic, strong) AFHTTPRequestOperationManager *requestManager;

@end

@implementation NetManager
#pragma mark - public Method
+ (instancetype)shareInstance {
    static NetManager *manager;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        manager = [[NetManager alloc] init];
    });
    return manager;
}

- (void)requestForRegisterWithNickName:(NSString *)nickName Email:(NSString *)email Psw:(NSString *)psw Block:(StateBlock)block{
    NSDictionary *dict = @{@"email" : email, @"password" : [self encodePsw:psw], @"nickname" : nickName};
    [self.requestManager POST:URL_FOR_REGISTER
                   parameters:dict
                      success:^(AFHTTPRequestOperation *operation, id responseObject) {
                          if (operation.response.statusCode == 201) {
                              if (block) {
                                  block(successful, nil);
                              }
                          } else {
                              if (block) {
                                  block(failed, nil);
                              }
                          }
                      }
                      failure:^(AFHTTPRequestOperation *operation, NSError *error) {
                          if (block) {
                              block(failed, nil);
                          }
                      }];
}

- (void)requestForSignInWithEmail:(NSString *)email Psw:(NSString *)psw Block:(StateBlock)block {
    NSDictionary *dict = @{@"email" : email, @"password" : [[NetManager shareInstance] encodePsw:psw]};
    [self.requestManager POST:URL_FOR_SIGNIN
                   parameters:dict
                      success:^(AFHTTPRequestOperation *operation, id responseObject) {
                          if (operation.response.statusCode == 200) {
                              if (block) {
                                  NSDictionary *dict = @{@"token": operation.response.allHeaderFields[@"X-Hoocal-Token"]};
                                  block(successful, dict);
                              }
                          } else {
                              if (block) {
                                  block(failed, nil);
                              }
                          }
                      }
                      failure:^(AFHTTPRequestOperation *operation, NSError *error) {
                          if (block) {
                              block(failed, nil);
                          }
                      }];
}

- (void)requestForCreateEventWithDict:(NSDictionary *)dict Block:(StateBlock)block {
    [self.requestManager POST:URL_FOR_CREATE_EVENT
                   parameters:dict
                      success:^(AFHTTPRequestOperation *operation, id responseObject) {
                          
                      }
                      failure:^(AFHTTPRequestOperation *operation, NSError *error) {
                          
                      }];
}

#pragma mark - access method
- (AFHTTPRequestOperationManager *)requestManager {
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        _requestManager = [AFHTTPRequestOperationManager manager];
        _requestManager.requestSerializer = [AFJSONRequestSerializer serializer];
        
    });
    return _requestManager;
}

- (NSString *)encodePsw:(NSString *)psw {
    NSString *md5 = [CocoaSecurity md5:psw].hexLower;
    return [CocoaSecurity md5:[md5 stringByAppendingString:@"hooCal"]].hexLower;
}

@end
