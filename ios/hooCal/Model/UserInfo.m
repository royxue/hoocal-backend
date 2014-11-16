//
//  UserInfo.m
//  hooCal
//
//  Created by zhongtoby on 14/11/15.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import "UserInfo.h"

@implementation UserInfo
+ (NSString *)primaryKey {
    return @"Email";
}
+ (NSDictionary *)defaultPropertyValues {
    return @{@"nickName":@""};
}
@end
